import yaml


def main():
    with open("config.yaml") as file:
        config = yaml.safe_load(file)
    with open("ios-themes/ios-themes.yaml") as file:
        base_theme = yaml.safe_load(file).get("ios-dark-mode-blue-red")

    themes_content = {}

    for theme in config.get("themes"):
        new_theme = base_theme.copy()

        for var, value in config.get("global", {}).items():
            new_theme[var] = value

        theme_vars = config.get("themes").get(theme)

        background = theme_vars.get("background", "homekit-bg-blue-red.jpg")
        background_string = f"center / cover no-repeat fixed url('/hacsfiles/themes/backgrounds/{background}')"
        theme_vars["background-image"] = background_string
        theme_vars.pop("background", None)

        for var, value in theme_vars.items():
            new_theme[var] = value

        themes_content[theme] = new_theme

    with open("themes.yaml", "w") as file:
        yaml.safe_dump(themes_content, file)


if __name__ == "__main__":
    main()
