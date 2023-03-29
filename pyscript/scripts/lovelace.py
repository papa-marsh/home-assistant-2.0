from datetime import date, datetime
from dateutil import tz
import constants
import format


@time_trigger("startup")
def persist_sidebar_text():
    state.persist("pyscript.sidebar_text", default_value="")


@time_trigger("startup", "cron(*/15 0 * * *)")
@state_trigger("calendar.warnersfam_gmail_com.start_time", "sun.sun")
def set_sidebar_text():
    sun_action = "sets" if sun.sun == "above_horizon" else "rises"
    sun_time = (
        sun.sun.next_setting if sun.sun == "above_horizon" else sun.sun.next_rising
    )
    sun_time = datetime.strftime(
        datetime.fromisoformat(sun_time).astimezone(tz.tzlocal()), "%-I:%M %p"
    )

    start_time = datetime.strptime(
        calendar.warnersfam_gmail_com.start_time, "%Y-%m-%d %H:%M:%S"
    )
    next_up = f"Next up is {calendar.warnersfam_gmail_com.message}, {format.colloquial_date(start_time.date())}"
    if not calendar.warnersfam_gmail_com.all_day:
        next_up += f" at {datetime.strftime(start_time, '%-I:%M %p')}"

    pyscript.sidebar_text = f"""
        <li>Happy {date.today().strftime('%A')}!</li>
        <li>The sun {sun_action} at {sun_time}.</li>
        <li>‎</li>
        <li>{next_up}.</li>
    """


@time_trigger("startup")
def persist_chelsea_next_fixture():
    state.persist(
        "pyscript.chelsea_next_fixture",
        default_value=datetime.today().isoformat(),
        default_attributes={
            "home_team": "Home",
            "away_team": "Away",
            "competition": "",
            "date": "Date",
            "time": "Time",
            "home_path": f"/local/PL/Default.png",
            "away_path": f"/local/PL/Default.png",
            "top_row": "",
        },
    )


@time_trigger("startup", "cron(*/15 0 * * *)")
@state_trigger("calendar.chelsea_fixtures.start_time")
def set_chelsea_fixture_card():
    description = calendar.chelsea_fixtures.description.split("\n")
    home = description[0].split(" v ")[0]
    away = description[0].split(" v ")[1]
    start = datetime.strptime(calendar.chelsea_fixtures.start_time, "%Y-%m-%d %H:%M:%S")

    state.set(
        "pyscript.chelsea_next_fixture",
        value=datetime.today(),
        home_team=home,
        away_team=away,
        competition=description[2],
        top_row=description[2],
        date=format.colloquial_date(start.date()),
        time=start.time().strftime("%-I:%M %p"),
        home_path=f"/local/PL/{home}.png"
        if home in constants.SOCCER_CRESTS
        else "/local/PL/Default.png",
        away_path=f"/local/PL/{away}.png"
        if away in constants.SOCCER_CRESTS
        else "/local/PL/Default.png",
    )


@service("lovelace.chelsea_fixture_tap")
@task_unique("chelsea_fixture_tap")
def chelsea_fixture_tap():
    pyscript.chelsea_next_fixture.top_row = (
        pyscript.chelsea_next_fixture.home_team
        if pyscript.chelsea_next_fixture.home_team != "Chelsea"
        else pyscript.chelsea_next_fixture.away_team
    )
    task.sleep(5)
    pyscript.chelsea_next_fixture.top_row = pyscript.chelsea_next_fixture.competition
