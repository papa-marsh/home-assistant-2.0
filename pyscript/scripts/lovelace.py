from datetime import date, datetime
import constants
import dates
import util


@time_trigger("startup")
def persist_sidebar_text():
    state.persist("pyscript.sidebar_text", default_value="")


@time_trigger("startup", "cron(*/10 * * * *)")
@state_trigger("calendar.warnersfam_gmail_com.start_time", "sun.sun")
def set_sidebar_text():
    sun_action = "sets" if sun.sun == "above_horizon" else "rises"
    sun_time = sun.sun.next_setting if sun.sun == "above_horizon" else sun.sun.next_rising
    sun_time = dates.parse_timestamp(sun_time, output_format="time")

    event = util.get_calendar_events(days=7, next_only=True, ignore_ongoing=True)
    start = dates.parse_timestamp(event["start"])

    next_up = f"Next up is {event['summary']}, {dates.colloquial_date(start.date())}"
    if "T" in event["start"]:
        next_up += f" at {dates.parse_timestamp(start, output_format='time')}"

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
        default_value=datetime.now().isoformat(),
        default_attributes={
            "home_team": "Home",
            "away_team": "Away",
            "competition": "",
            "date": "Date",
            "time": "Time",
            "home_path": "/local/PL/Default.png",
            "away_path": "/local/PL/Default.png",
            "top_row": "",
            "blink": False,
        },
    )


@time_trigger("startup", "cron(0 0 * * *)")
@state_trigger("calendar.chelsea_fixtures.start_time")
def set_chelsea_fixture_card():
    description = calendar.chelsea_fixtures.description.split("\n")
    home = description[0].split(" v ")[0]
    away = description[0].split(" v ")[1]
    start = datetime.strptime(calendar.chelsea_fixtures.start_time, "%Y-%m-%d %H:%M:%S")

    state.set(
        "pyscript.chelsea_next_fixture",
        value=datetime.now(),
        home_team=home,
        away_team=away,
        competition=description[2],
        top_row=description[2],
        date=dates.colloquial_date(start.date()),
        time=start.time().strftime("%-I:%M %p"),
        home_path=f"/local/PL/{home}.png"
        if home in constants.SOCCER_CRESTS
        else "/local/PL/Default.png",
        away_path=f"/local/PL/{away}.png"
        if away in constants.SOCCER_CRESTS
        else "/local/PL/Default.png",
    )


@service("pyscript.chelsea_fixture_tap")
def chelsea_fixture_tap():
    task.unique("chelsea_fixture_tap")
    pyscript.chelsea_next_fixture.top_row = (
        pyscript.chelsea_next_fixture.home_team
        if pyscript.chelsea_next_fixture.home_team != "Chelsea"
        else pyscript.chelsea_next_fixture.away_team
    )
    task.sleep(5)
    pyscript.chelsea_next_fixture.top_row = pyscript.chelsea_next_fixture.competition


# @service("pyscript.chelsea_fixture_double_tap")
# def chelsea_fixture_double_tap():
