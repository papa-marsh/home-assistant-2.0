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
        },
    )


# @state_trigger("")
# def is_playlist_saved():
#     pass


# def speaker_volume_sync():
#     pass
