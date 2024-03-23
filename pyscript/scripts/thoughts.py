from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules.dummy import *
    from ..modules.files import File
    from ..modules.push import Notification
else:
    from files import File
    from push import Notification


@event_trigger("new_thought")
def create_thought(**kwargs):
    thought = kwargs["thought"].replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    today = datetime.today().strftime('%Y/%m/%d')
    file = File("thoughts")

    key_list = ["Daily Thoughts", today, "Thoughts"]

    today_thoughts = file.read(key_list, [])
    today_thoughts.append(thought)

    file.write(key_list, today_thoughts)


def morning_review():
    ...
