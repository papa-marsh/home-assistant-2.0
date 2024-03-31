from datetime import date, datetime, timedelta
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import dates, util
    from ..modules.dummy import *
else:
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
            "home_path": "/local/soccer_badges/Default.png",
            "away_path": "/local/soccer_badges/Default.png",
            "top_row": "",
            "blink": False,
        },
    )


@time_trigger("startup", "cron(0 0 * * *)")
@state_trigger("calendar.chelsea_fixtures.start_time")
def set_chelsea_fixture_card():
    try:
        description = calendar.chelsea_fixtures.description.split("\n")
        home = description[0].split(" v ")[0]
        away = description[0].split(" v ")[1]
        start = datetime.strptime(calendar.chelsea_fixtures.start_time, "%Y-%m-%d %H:%M:%S")
        badge = os.listdir("/config/www/soccer_badges")

        state.set(
            "pyscript.chelsea_next_fixture",
            value=datetime.now(),
            home_team=home,
            away_team=away,
            competition=description[2],
            top_row=description[2],
            date=dates.colloquial_date(start.date()),
            time=start.time().strftime("%-I:%M %p"),
            home_path=f"/local/soccer_badges/{home}.png" if f"{home}.png" in badge else "/local/soccer_badges/Default.png",
            away_path=f"/local/soccer_badges/{away}.png" if f"{away}.png" in badge else "/local/soccer_badges/Default.png",
        )
    except:
        state.set(
            "pyscript.chelsea_next_fixture",
            home_team="",
            away_team="",
            competition="",
            top_row="",
            date="Unavailable",
            time="",
            home_path="/local/soccer_badges/Default.png",
            away_path="/local/soccer_badges/Default.png",
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


@time_trigger("startup", "cron(*/5 * * * *)")
@state_trigger("calendar.chelsea_fixtures.start_time")
def chelsea_fixture_blink():
    try:
        start = datetime.strptime(calendar.chelsea_fixtures.start_time, "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= start - timedelta(minutes=10):
            if not pyscript.chelsea_next_fixture.blink:
                pyscript.chelsea_next_fixture.blink = True
        else:
            pyscript.chelsea_next_fixture.blink = False
    except:
        pyscript.chelsea_next_fixture.blink = False
