from datetime import datetime
import format

state.persist(
    "pyscript.chelsea_next_fixture",
    default_value=datetime.today().isoformat(),
    default_attributes={
        "home_team": "Home",
        "away_team": "Away",
        "competition": "Competition",
        "date": "Date",
        "time": "Time",
        "home_path": f"/local/PL/Default.png",
        "away_path": f"/local/PL/Default.png",
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
        date=format.colloquial_date(start.date()),
        time=start.time().strftime("%-H:%M %p"),
        home_path=f"/local/PL/{home}.png",
        away_path=f"/local/PL/{away}.png",
    )
