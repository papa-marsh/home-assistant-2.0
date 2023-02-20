import yaml


def generate_all():
    with open("entity-map.yaml") as f:
        entity_map = yaml.safe_load(f)

    for index in entity_map:
        generate_card(index, entity_map[index])


def generate_card(location, entity):
    if entity == "placeholder":
        with open("placeholder.yaml") as f:
            card_yaml = yaml.safe_load(f)

    else:
        with open("template.yaml") as f:
            card_yaml = yaml.safe_load(f)
            card_yaml["entity"] = "pyscript.entity_card_" + entity

    with open("card-" + str(location) + ".yaml", "w") as f:
        yaml.dump(card_yaml, f, default_flow_style=False)


if __name__ == "__main__":
    generate_all()
