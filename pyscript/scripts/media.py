# TODO iOS action that set all volume to most recent changed

# TODO highlight button to save/unsave current playlist

# TODO helper (speaker group may be better?) input slider to set all volumes


@time_trigger("startup")
def persist_media_card():
    state.persist(
        "pyscript.media_card",
        default_value="controls",
        default_attributes={
            "saved": False,
            "synced": False,
            "save_icon": "mdi:playlist-plus",
            "save_text": "Save",
            "sync_icon": "mdi:music-box-multiple-outline",
            "sync_text": "Sync",
        },
    )


@service("lovelace.media_card_save")
def media_card_save():
    # TODO
    pyscript.media_card.saved = not pyscript.media_card.saved


@service("lovelace.media_card_sync")
def media_card_sync():
    # TODO
    pyscript.media_card.synced = not pyscript.media_card.synced


@service("lovelace.media_card_more")
def media_card_more():
    pyscript.media_card = "volume" if pyscript.media_card == "controls" else "controls"


@state_trigger("pyscript.media_card.saved")
def update_save_button():
    if pyscript.media_card.saved:
        pyscript.media_card.save_icon = "mdi:playlist-star"
        pyscript.media_card.save_text = "Saved"
    else:
        pyscript.media_card.save_icon = "mdi:playlist-plus"
        pyscript.media_card.save_text = "Save"


@state_trigger("pyscript.media_card.syncd")
def update_sync_button():
    if pyscript.media_card.syncd:
        pyscript.media_card.sync_icon = "mdi:music-box-multiple"
        pyscript.media_card.sync_text = "Syncd"
    else:
        pyscript.media_card.sync_icon = "mdi:music-box-multiple-outline"
        pyscript.media_card.sync_text = "Sync"


def is_playlist_saved(playlist):
    pass
