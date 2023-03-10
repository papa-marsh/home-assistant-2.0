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
    return


@service("lovelace.media_card_sync")
def media_card_sync():
    return


@service("lovelace.media_card_more")
def media_card_more():
    pyscript.media_card = "volume" if pyscript.media_card == "controls" else "controls"


# @state_trigger("")
# def is_playlist_saved():
#     pass


# def speaker_volume_sync():
#     pass
