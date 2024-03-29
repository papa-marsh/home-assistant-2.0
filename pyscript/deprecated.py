# home.py 2023-08-01
# @time_trigger("startup", "cron(0 0,19 * * *)")
# @state_trigger("binary_sensor.emily_s_iphone_focus")
# def entity_card_update_row_3():
#     task.unique("home_entity_card_update_row_3")
#     if binary_sensor.emily_s_iphone_focus == "on" and 9 <= datetime.now().hour < 18:
#         pyscript.entity_card_home.row_3_value = dates.format_duration(
#             binary_sensor.emily_s_iphone_focus.last_changed
#         )
#         pyscript.entity_card_home.row_3_icon = "mdi:bed-clock"
#         task.sleep(60)
#         entity_card_update_row_3()
#     else:
#         now = datetime.now()
#         next_bin_day = get_next_bin_day()
#         if next_bin_day == now.date() and now.hour >= 18:
#             pyscript.entity_card_home.blink = True
#         pyscript.entity_card_home.row_3_value = dates.date_countdown(next_bin_day)
#         pyscript.entity_card_home.row_3_icon = "mdi:delete"


# home.py 2023-08-01
# def get_next_bin_day():
#     next_bin_day = dates.get_next_weekday("mon")
#     if "last_bin_day" not in pyscript.entity_card_home.staging:
#         pyscript.entity_card_home.staging["last_bin_day"] = date.today() - timedelta(
#             days=7
#         )
#     if isinstance(pyscript.entity_card_home.staging["last_bin_day"], str):
#         pyscript.entity_card_home.staging["last_bin_day"] = datetime.strptime(
#             pyscript.entity_card_home.staging["last_bin_day"], "%Y-%m-%d"
#         ).date()
#     if next_bin_day <= pyscript.entity_card_home.staging["last_bin_day"]:
#         next_bin_day += timedelta(days=7)
#
#     return next_bin_day


# home.py 2023-08-01
# @service("pyscript.home_hold")
# def entity_card_hold():
#     pyscript.entity_card_home.staging["last_bin_day"] = date.today()
#     pyscript.entity_card_home.blink = False
#     entity_card_update_row_3()


# @state_trigger("sensor.marshall_s_iphone_battery_state")
# def set_master_sound_machine(**kwargs):
#     if kwargs["value"] == "Not Charging":
#         switch.turn_off(entity_id="switch.master_sound_machine")
#     else:
#         switch.turn_on(entity_id="switch.master_sound_machine")


# @state_trigger("switch.ellies_sound_machine in ['on', 'off']")
# def send_sleep_notification():
#     wakeup = switch.ellies_sound_machine == "off"
#     noti = push.Notification(
#         title="Wakeup Time" if wakeup else "Sleep Time",
#         message=f"Ellie {'got up' if wakeup else 'went down'} at {dates.parse_timestamp(output_format='time')}",
#         tag="sleepy_wake_time",
#         group="sleepy_wake_time",
#         target="marshall",
#     )
#     if wakeup:
#         noti.message += (
#             f" after {dates.format_duration(pyscript.vars.sleepy_time_timestamp)}"
#         )
#     noti.send()


# @time_trigger("startup")
# @state_trigger("switch.ellies_sound_machine")
# def entity_card_update_row_3():
#     task.unique("home_entity_card_update_row_3")
#     if switch.ellies_sound_machine == "on":
#         pyscript.entity_card_home.row_3_icon = "mdi:sleep"
#         while True:
#             pyscript.entity_card_home.row_3_value = dates.format_duration(
#                 switch.ellies_sound_machine.last_changed
#             )
#             task.sleep(60)
#     else:
#         pyscript.entity_card_home.row_3_icon = "mdi:bed-clock"


# service: spotcast.start
# data:
#   spotify_device_id: 35f8cd3045279d156ec424531e7301e1fbc3d56f
#   shuffle: true
#   repeat: false
#   random_song: true
#   force_playback: true


# @time_trigger("cron(0 9 * * 1-5)")
# def entity_card_update_row_3():
#     pyscript.entity_card_office.blink = True
#     pyscript.entity_card_office.row_3_value = dates.date_countdown(get_next_timecard())


# def get_next_timecard():
#     next_timecard = dates.get_next_weekday("fri")
#     if "last_timecard" not in pyscript.entity_card_office.staging:
#         pyscript.entity_card_office.staging["last_timecard"] = date.today() - timedelta(days=7)
#     if isinstance(pyscript.entity_card_office.staging["last_timecard"], str):
#         pyscript.entity_card_office.staging["last_timecard"] = datetime.strptime(
#             pyscript.entity_card_office.staging["last_timecard"],
#             "%Y-%m-%d"
#         ).date()
#     elif next_timecard <= pyscript.entity_card_office.staging["last_timecard"]:
#         next_timecard += timedelta(days=7)
# 
#     return next_timecard


# @state_trigger("binary_sensor.chelsea_cabinet_sensor=='on'")
# def chelsea_double_meal_warning():
#     task.unique("chelsea_double_meal", kill_me=True)
#     now = datetime.now().astimezone(tz.tzlocal())
#     last_opened = binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tz.tzlocal())
#     if last_opened > now - timedelta(hours=2):
#         noti = push.Notification(
#             title="Beth Already Ate!",
#             message=f"Don't let her trick you. Double check before feeding Beth {'breakfast' if datetime.now().hour < 12 else 'dinner'}",
#             tag="double_feed_warning",
#             group="double_feed_warning",
#             priority="time-sensitive",
#             target="marshall" if person.marshall == "home" and person.emily != "home" else "all",
#         )
#         noti.send()
#     task.sleep(5 * 60)
