import constants


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
        },
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
    "media_player.basement.volume_level",
    "pyscript.media_card.sync",
)
@task_unique("sync_speaker_volume")
def sync_volume(target="media_player.living_room.volume_level", **kwargs):
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
