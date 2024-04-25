from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import constants, dates, secrets
    from ..modules.dummy import *
    from ..modules.push import Notification
else:
    import constants
    import dates
    from push import Notification
    import secrets


@event_trigger("emilys_playlist")
def play_emilys_playlist(**kwargs):
    caller = kwargs['caller']
    if state.get(f"person.{caller}") == "home":
        input_select.select_option(entity_id="input_select.media_card_playlist", option="Emily's Playlist")
    else:
        noti = Notification(
            title="Command Failed",
            target=caller,
            priority="time-sensitive",
            message=f"You must be home to start Emily's Playlist",
        )
        noti.send()


@event_trigger("ellies_playlist")
def play_ellies_playlist(**kwargs):
    caller = kwargs['caller']
    if state.get(f"person.{caller}") == "home":
        input_select.select_option(entity_id="input_select.media_card_playlist", option="Songs")
    else:
        noti = Notification(
            title="Command Failed",
            target=caller,
            priority="time-sensitive",
            message=f"You must be home to start Ellie's Playlist",
        )
        noti.send()


@time_trigger("cron(0 4 * * *)")
def reset_media_controls():
    media_player.media_pause(entity_id=constants.SPEAKER_GROUP + ["media_player.office"])
    media_player.volume_mute(entity_id=constants.SPEAKER_GROUP + ["media_player.office"], is_volume_muted=False,)

    pyscript.media_card.group = True
    pyscript.media_card.sync = True
    pyscript.media_card = "controls"
    input_select.select_option(entity_id="input_select.media_card_playlist", option="None Selected")

    media_player.volume_set(entity_id=constants.SPEAKER_GROUP, volume_level=0.3)
    media_player.volume_set(entity_id="media_player.office", volume_level=0.35)
    media_player.volume_set(entity_id="media_player.living_room_tv", volume_level=0.1)


@state_trigger("switch.ellies_sound_machine=='on'")
def bedtime_speaker_volume():
    if person.emily != secrets.IN_LAWS_ZONE:
        media_player.volume_set(entity_id="media_player.office", volume_level=0.22)
        media_player.volume_set(entity_id=constants.SPEAKER_GROUP, volume_level=0.3)


@time_trigger("startup")
def persist_media_card():
    state.persist(
        "pyscript.media_card",
        default_value="controls",
        default_attributes={
            "group": False,
            "sync": False,
            "group_icon": "mdi:speaker",
            "group_text": "Group",
            "sync_icon": "mdi:volume-source",
            "sync_text": "Sync",
            "current_playlist": "None Selected",
        },
    )


@time_trigger("startup")
@state_trigger("media_player.living_room.media_playlist", "sensor.sonos_favorites")
def set_media_card_playlists():
    task.unique("set_media_card_playlists")
    now = dates.now()
    sonos_integration_id = "5710f1a75e16bd6a0b67108a0d28adbe"
    
    if not isinstance(pyscript.vars.sonos_last_reload, datetime):
        pyscript.vars.sonos_last_reload = now

    seconds_since_reload = (now - pyscript.vars.sonos_last_reload).seconds

    try:
        sensor.sonos_favorites.items
    except:
        hass_startup_time = dates.parse_timestamp(sensor.home_assistant_uptime, output_format=datetime)
        if seconds_since_reload > 3600 and now - hass_startup_time > timedelta(minutes=10):
            pyscript.vars.sonos_last_reload = now
            homeassistant.reload_config_entry(entry_id=sonos_integration_id)
        return

    options = [sensor.sonos_favorites.items[source] for source in sensor.sonos_favorites.items]

    if "media_playlist" not in state.getattr("media_player.living_room"):
        playlist = "None Selected"
        options = [playlist] + options
    elif media_player.living_room.media_playlist not in options:
        playlist = f"{media_player.living_room.media_playlist} (not saved)"
        options = [playlist] + options
    else:
        playlist = media_player.living_room.media_playlist
        options = ["None Selected"] + options

    if options[0] == "None Selected":
        task.sleep(5)

    input_select.set_options(entity_id="input_select.media_card_playlist", options=options, blocking=True)
    input_select.select_option(entity_id="input_select.media_card_playlist", option=playlist)


@state_trigger("input_select.media_card_playlist != 'None Selected'")
def play_media_card_playlist():
    hass_startup_time = dates.parse_timestamp(sensor.home_assistant_uptime, output_format=datetime)
    if dates.now() - hass_startup_time < timedelta(seconds=120):
        return

    current_playlist = media_player.living_room.media_playlist if "media_playlist" in media_player.living_room else None
    if current_playlist != input_select.media_card_playlist:
        media_player.shuffle_set(entity_id=constants.SPEAKER_GROUP, shuffle=True)
        media_player.repeat_set(entity_id=constants.SPEAKER_GROUP, repeat="all")
        media_player.select_source(entity_id="media_player.living_room", source=input_select.media_card_playlist)


@service("pyscript.media_card_group")
def media_card_group():
    pyscript.media_card.group = not pyscript.media_card.group


@service("pyscript.media_card_sync")
def media_card_sync():
    pyscript.media_card.sync = not pyscript.media_card.sync


@service("pyscript.media_card_more")
def media_card_more():
    pyscript.media_card = "volume" if pyscript.media_card == "controls" else "controls"


@state_trigger("pyscript.media_card.group")
def update_group_button():
    if pyscript.media_card.group:
        pyscript.media_card.group_icon = "mdi:speaker-multiple"
        pyscript.media_card.group_text = "Grouped"
    else:
        pyscript.media_card.group_icon = "mdi:speaker"
        pyscript.media_card.group_text = "Group"


@state_trigger("pyscript.media_card.sync")
def update_sync_button():
    if pyscript.media_card.sync:
        pyscript.media_card.sync_icon = "mdi:volume-equal"
        pyscript.media_card.sync_text = "Synced"
        sync_volume()
    else:
        pyscript.media_card.sync_icon = "mdi:volume-source"
        pyscript.media_card.sync_text = "Sync"


@state_trigger("media_player.living_room.group_members", "pyscript.media_card.group")
def join_to_group():
    if pyscript.media_card.group and len(media_player.living_room.group_members) < len(constants.SPEAKER_GROUP):
        group_speakers()


@state_trigger(
    "media_player.living_room.volume_level",
    "media_player.front_room.volume_level",
    "media_player.craft_room.volume_level",
)
def sync_volume(target="media_player.living_room", **kwargs):
    task.unique("sync_speaker_volume")
    if not pyscript.media_card.sync:
        return
    task.sleep(0.2)
    if kwargs:
        target = kwargs["var_name"]
    volume = state.getattr(target)["volume_level"]
    for speaker in constants.SPEAKER_GROUP:
        if speaker != target:
            media_player.volume_set(entity_id=speaker, volume_level=volume)


def group_speakers(target="media_player.living_room"):
    for speaker in constants.SPEAKER_GROUP:
        if state.get(speaker) == "playing":
            media_player.join(entity_id=speaker, group_members=constants.SPEAKER_GROUP)
            break
    else:
        media_player.join(
            entity_id=target,
            group_members=constants.SPEAKER_GROUP,
        )


def ungroup_speakers(target=None):
    if target:
        media_player.unjoin(entity_id=target)
    else:
        for speaker in constants.SPEAKER_GROUP:
            media_player.unjoin(entity_id=speaker)
