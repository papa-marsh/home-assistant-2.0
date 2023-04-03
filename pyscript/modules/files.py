import yaml
import constants


@pyscript_executor
def read_file(file_name):
    with open(f"{constants.BASE_FILE_PATH}{file_name}") as f:
        if ".yaml" in file_name:
            contents = yaml.safe_load(f)
        else:
            contents = f.read()

    return contents


def zone_short_name(zone_name):
    zones = read_file("zones.yaml")
    if zone_name in zones and "short_name" in zones[zone_name]:
        name = zones[zone_name]["short_name"]
    else:
        name = zone_name

    return name
