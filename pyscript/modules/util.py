from datetime import date, timedelta


def get_next_weekday(day):
    today = date.today()
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    try:
        day = int(day)
    except:
        day = day_map[day.lower()]

    return today + timedelta((day - today.weekday()) % 7)
