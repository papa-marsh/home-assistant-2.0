import constants


@time_trigger("cron(0 4 * * *)")
def reset_media_controls():
    media_player.media_pause(entity_id=constants.SPEAKER_GROUP)
    media_player.volume_mute(
        entity_id=constants.SPEAKER_GROUP,
        is_volume_muted=False,
    )
    media_player.volume_set(entity_id=constants.SPEAKER_GROUP, volume_level=0.3)
    pyscript.media_card.group = True
    pyscript.media_card.sync = True
    pyscript.media_card = "controls"

    media_player.volume_set(entity_id="media_player.living_room_tv", volume_level=0.08)
    media_player.media_pause(entity_id="media_player.office")
    media_player.volume_mute(entity_id="media_player.office", is_volume_muted=False)
    media_player.volume_set(entity_id="media_player.office", volume_level=0.2)


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
    options = [
        sensor.sonos_favorites.items[source] for source in sensor.sonos_favorites.items
    ]

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

    input_select.set_options(
        entity_id="input_select.media_card_playlist",
        options=options,
        blocking=True,
        limit=5,
    )
    input_select.select_option(
        entity_id="input_select.media_card_playlist", option=playlist
    )


@time_trigger("startup")
@state_trigger("input_select.media_card_playlist != 'None Selected'")
def play_media_card_playlist():
    if (
        "media_playlist" in media_player.living_room
        and media_player.living_room.media_playlist != input_select.media_card_playlist
    ):
        media_player.select_source(
            entity_id="media_player.living_room",
            source=input_select.media_card_playlist,
        )


@service("lovelace.media_card_group")
def media_card_group():
    pyscript.media_card.group = not pyscript.media_card.group


@service("lovelace.media_card_sync")
def media_card_sync():
    pyscript.media_card.sync = not pyscript.media_card.sync


@service("lovelace.media_card_more")
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
    if pyscript.media_card.group and len(media_player.living_room.group_members) < len(
        constants.SPEAKER_GROUP
    ):
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
