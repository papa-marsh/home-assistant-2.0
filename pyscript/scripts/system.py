@time_trigger("cron(0 * * * *)")
def restart_ssh_addon():
    hassio.addon_restart(addon="a0d7b954_ssh")
