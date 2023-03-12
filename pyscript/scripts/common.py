@time_trigger("startup")
def persist_mutex():
    state.persist(
        "pyscript.mutex",
        default_value="",
        default_attributes={
            "media_group": False,
            "media_sync": False,
        },
    )


def mutex(func, *args, **kwargs):
    # TODO
    pass
