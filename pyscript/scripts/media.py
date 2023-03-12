import constants


@time_trigger("startup")
def persist_media_card():
    state.persist(
        "pyscript.media_card",
        default_value="controls",
        default_attributes={
            "grouped": False,
            "synced": False,
            "group_icon": "mdi:speaker",
            "group_text": "Group",
            "sync_icon": "mdi:music-box-multiple-outline",
            "sync_text": "Sync",
        },
    )


@service("lovelace.media_card_group")
def media_card_group():
    pyscript.media_card.grouped = not pyscript.media_card.grouped


@service("lovelace.media_card_sync")
def media_card_sync():
    # TODO
    pyscript.media_card.synced = not pyscript.media_card.synced


@service("lovelace.media_card_more")
def media_card_more():
    pyscript.media_card = "volume" if pyscript.media_card == "controls" else "controls"


@state_trigger("pyscript.media_card.grouped")
def update_group_button():
    if pyscript.media_card.grouped:
        pyscript.media_card.group_icon = "mdi:speaker-multiple"
        pyscript.media_card.group_text = "Grouped"
    else:
        pyscript.media_card.group_icon = "mdi:speaker"
        pyscript.media_card.group_text = "Group"


@state_trigger("pyscript.media_card.synced")
def update_sync_button():
    if pyscript.media_card.synced:
        pyscript.media_card.sync_icon = "mdi:music-box-multiple"
        pyscript.media_card.sync_text = "Synced"
    else:
        pyscript.media_card.sync_icon = "mdi:music-box-multiple-outline"
        pyscript.media_card.sync_text = "Sync"


@state_trigger("media_player.living_room.group_members", "pyscript.media_card.grouped")
def join_to_group():
    if pyscript.media_card.grouped and len(
        media_player.living_room.group_members
    ) < len(constants.SPEAKER_GROUP):
        group_speakers()


@state_trigger(
    "media_player.living_room.volume_level",
    "media_player.front_room.volume_level",
    "media_player.craft_room.volume_level",
    "media_player.basement.volume_level",
)
@task_unique("sync_speaker_volume")
def sync_volume(target="media_player.living_room.volume_level"):
    log.warning(kwargs)
    # for speaker in constants.SPEAKER_GROUP:


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
