from datetime import date, datetime, timedelta
from typing import Any, Literal, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..modules import dates
    from ..modules.dummy import *
    from ..modules.files import File
    from ..modules.push import Notification
else:
    import dates
    from files import File
    from push import Notification


STATE_SYMBOLS = {
    "pending": "🔷",
    "active": "🔶",
    "save": "✅",
    "skip": "❌"
}


@time_trigger("startup")
def persist_thinker():
    state.persist(
        "pyscript.thinker",
        default_value="off",
        default_attributes={
            "review_thoughts": {},
            "review_markdown": "",
            "review_index": 0,
            "ready_to_commit": False,
            "last_reminder": None
        },
    )
    state.persist(
        "pyscript.thinker_edit_thought",
        default_value="off",
    )


@event_trigger("new_thought")
def new_thought(**kwargs: dict[Any, Any]) -> None:
    thought = kwargs["thought"].replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    today = date.today()
    file = File("thinker")

    key_list = ["daily_thoughts", today, "thoughts"]

    today_thoughts = file.read(key_list, [])
    today_thoughts.append(thought)

    file.write(key_list, today_thoughts)
    set_reviewed_status(reviewed=False)


def set_reviewed_status(reviewed: bool, date_key: date | None = None) -> None:
    """
    Sets a day's raw thoughts to 'reviewed' in the "daily_thoughts" thinker yaml file.
    'date_key' should be a date object.
    """
    date_key = date_key or date.today()
    key_list = ["daily_thoughts", date_key, "reviewed"]

    File("thinker").write(key_list, reviewed)


@time_trigger("cron(25 9 * * 1-5)")
def daily_review() -> None:
    thought_count = populate_review_thoughts()

    if thought_count:
        noti = Notification(
            title="New Thoughts!",
            message="Tap to review",
            url="thinker",
            group="daily_thought_review",
            tag="daily_thought_review",
            sound="Alert_ActivityGoalAttained_Haptic.caf",
            target="marshall",
        )
        noti.send()


def populate_review_thoughts() -> int:
    """
    Scans for the chronologically first unreviewed day (excluding today).
    Loads its thoughts into the pyscript.thinker entity.
    Returns the number of thoughts populated.
    """
    file = File("thinker")
    raw_thoughts = file.read(["daily_thoughts"])
    review_thoughts = []

    for date_key, contents in raw_thoughts.items():
        if date_key != date.today() and not contents["reviewed"]:
            for index, thought in enumerate(contents["thoughts"]):
                review_thoughts.append({
                    "index": index,
                    "date": date_key,
                    "thought": thought,
                    "state": "active" if index == 0 else "pending"
                })

            break

    pyscript.thinker.ready_to_commit = False
    pyscript.thinker.review_thoughts = review_thoughts
    pyscript.thinker.review_index = 0
    pyscript.thinker = "on" if review_thoughts else "off"
    
    populate_review_markdown()

    return len(review_thoughts)


def populate_review_markdown() -> None:
    if not pyscript.thinker.review_thoughts:
        pyscript.thinker.review_markdown = (
            "# Nothing to Review!\n"
            "### Time to do some thinking..."
        )
        return

    date_key = pyscript.thinker.review_thoughts[0]["date"]
    day_of_week = date_key.strftime("%A")
    colloquial_date = dates.colloquial_date(date_key, ordinals=True)

    markdown_content = (
        "# New Thoughts to Review!\n"
        f"## {day_of_week}, {colloquial_date}")

    for thought_data in pyscript.thinker.review_thoughts:
        symbol = STATE_SYMBOLS[thought_data["state"]]
        markdown_content += f"\n\n{symbol} {thought_data["thought"]}"

    pyscript.thinker.review_markdown = markdown_content
    pyscript.thinker_edit_thought = "off"

@service("thinker.review_thought")
def review_thought(state: Literal["save", "skip"]) -> None:
    if pyscript.thinker.review_index >= len(pyscript.thinker.review_thoughts):
        return

    pyscript.thinker.review_thoughts[pyscript.thinker.review_index]["state"] = state
    pyscript.thinker.review_index += 1

    if pyscript.thinker.review_index < len(pyscript.thinker.review_thoughts):
        pyscript.thinker.review_thoughts[pyscript.thinker.review_index]["state"] = "active"
    else:
        pyscript.thinker.ready_to_commit = True

    populate_review_markdown()


@service("thinker.edit_thought")
def edit_thought() -> None:
    index = pyscript.thinker.review_index
    
    if pyscript.thinker_edit_thought == "on":
        input_text.thinker_edit_thought = ""
        pyscript.thinker_edit_thought = "off"
    else:
        input_text.thinker_edit_thought = pyscript.thinker.review_thoughts[index]["thought"]
        pyscript.thinker_edit_thought = "on"
    


@service("thinker.confirm_edit")
def confirm_edit() -> None:
    pyscript.thinker.review_thoughts.append({
        "index": len(pyscript.thinker.review_thoughts),
        "date": pyscript.thinker.review_thoughts[0]["date"],
        "thought": str(input_text.thinker_edit_thought),
        "state": "pending",
    })

    input_text.thinker_edit_thought = ""
    populate_review_markdown()


@service("thinker.reset_review")
def reset_review() -> None:
    populate_review_thoughts()


@service("thinker.commit_review")
def commit_review() -> None:
    date_key = pyscript.thinker.review_thoughts[0]["date"]
    file = File("thinker")
    persisted_thoughts = file.read(["persisted_thoughts"])

    for review_thought in pyscript.thinker.review_thoughts:
        if review_thought["state"] == "save":
            date_string = review_thought["date"].strftime("%Y/%m/%d")
            preprocessed_date = datetime.strptime(date_string, "%Y/%m/%d").date()

            persisted_thoughts.append({
                "date": preprocessed_date,
                "thought": review_thought["thought"],
                "reminder_count": 0,
                "last_reminder": None
            })
    
    file.write(["persisted_thoughts"], persisted_thoughts)

    set_reviewed_status(True, date_key)
    populate_review_thoughts()


def get_persisted_thought(track_access: bool = False) -> dict[str, str | int]:
    """
    Retrieves a persisted thought using a weighted random algorithm based
    on each thought's reminder count. Lower counts are more likely.
    Return value is the full dict of the thought with keys: date, thought, reminder_count.
    """
    file = File("thinker")
    thoughts = file.read(["persisted_thoughts"])
    max_count = 0

    for thought in thoughts:
        max_count = max(max_count, thought["reminder_count"])

    weights = [(max_count + 1) - thought["reminder_count"] for thought in thoughts]
    selection = random.choices(thoughts, weights=weights, k=1)[0]
    output = selection.copy()
    
    if track_access:
        selection_index = thoughts.index(selection)
        thoughts[selection_index]["reminder_count"] += 1
        thoughts[selection_index]["last_reminder"] = date.today()

        file.write(["persisted_thoughts"], thoughts)
    
    return output


@time_trigger("cron(* * * * *)")
def check_send_reminder() -> None:
    """
    On each minute of the day, randomly determine if we should send a reminder.
    The liklihood increases as the time since last reminder increases.
    """
    if not pyscript.thinker.last_reminder or not isinstance(pyscript.thinker.last_reminder, datetime):
        pyscript.thinker.last_reminder = dates.now() - timedelta(hours=3)

    elapsed_minutes = (dates.now() - pyscript.thinker.last_reminder).seconds / 60
    probability = (elapsed_minutes / 5000) ** 1.5

    if random.random() < probability:
        pyscript.thinker.last_reminder = dates.now()
        if 6 <= dates.now().hour < 22:
            send_reminder()


def send_reminder() -> None:
    thought = get_persisted_thought(track_access=True)
    seen_count = thought["reminder_count"] + 1
    first_seen = dates.colloquial_date(thought["date"])

    message = f"{thought['thought']}\n\n"
    message += "First time seen" if seen_count == 1 else f"Seen {seen_count} times"
    message += f" since {first_seen}"

    noti = Notification(
        title="Don't Forget...",
        message=message,
        group="thought_reminder",
        target="marshall",
        sound="HourlyChime_Haptic.caf"
    )
    # noti.add_action(id="thinker_reminder_more", title="More")
    # noti.add_action(id="thinker_reminder_less", title="Less")
    # noti.add_action(id="thinker_reminder_done", title="Done")
    noti.send()

    
