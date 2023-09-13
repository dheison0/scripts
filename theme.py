#!/usr/bin/env python3
# Utility to set XFCE theme

import argparse
import json
import subprocess
from os import environ, path
from time import localtime, tzset

NOTIFY_TITLE = "Theme Manager"
DEFAULT_ICON = "style"
CONFIG_PATH = path.join(environ.get("HOME", "/root"), ".config/themes.json")
try:
    config = json.load(open(CONFIG_PATH))
except:
    config = {"themes": {}, "enabled": ""}


class CommandFailed(Exception):
    pass


def notify(message: str, icon: str = DEFAULT_ICON):
    print(f'[THEME] {message}')
    subprocess.run(["notify-send", "-i", icon, NOTIFY_TITLE, message])


def cmd_run(cmd: str) -> tuple[int, str]:
    process = subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    code = process.returncode
    stderr = process.stderr.decode().strip()
    stdout = process.stdout.decode().strip()
    return code, (stdout if code == 0 else stderr).strip()


def get_properties(channel: str) -> list:
    """
    Retrieves a list of properties from the specified channel using the xfconf-query command.

    :param channel: a string representing the channel to retrieve properties from
    :type channel: str
    :return: a list of properties retrieved from the specified channel
    :rtype: list
    :raises ValueError: if the specified channel is not a valid channel
    """
    code, output = cmd_run(f"xfconf-query -c '{channel}' -l")
    if code != 0:
        raise ValueError(f"{channel} is not a valid channel")
    return output.split("\n")


def xfconf_get(channel: str, property: str) -> str:
    """
    This function retrieves the value of a property from the given XFCE channel using the `xfconf-query` command.

    :param channel: A string representing the XFCE channel to retrieve the property value from.
    :param property: A string representing the name of the property to retrieve the value of.
    :return: A string representing the value of the property.
    :raises: CommandFailed, if the `xfconf-query` command fails to execute.
    """
    code, output = cmd_run(f"xfconf-query -c '{channel}' -p '{property}'")
    if code != 0:
        raise CommandFailed(f"xfconf-query command failed: {output}")
    return output


def xfconf_set(channel: str, property_name: str, value: str):
    """
    Sets the value of a property in the Xfce settings channel.

    :param channel: The name of the channel.
    :type channel: str
    :param property_name: The name of the property.
    :type property_name: str
    :param value: The new value of the property.
    :type value: str
    :raises CommandFailed: If the `xfconf-query` command fails.
    """
    code, output = cmd_run(
        f"xfconf-query -c '{channel}' -p '{property_name}' -s '{value}'"
    )
    if code != 0:
        raise CommandFailed(f"xfconf-query command failed: {output}")


def set_theme(theme: dict):
    """
    Sets the theme for XFCE desktop environment by modifying various xfconf settings.

    :param theme: A dictionary containing the following keys:
        - 'gtk' (str): The name of the GTK theme.
        - 'xfwm' (Optional[str]): The name of the XFWM theme. If not provided, the GTK theme name will be used.
        - 'icons' (str): The name of the icon theme.
        - 'cursor' (str): The name of the cursor theme.
        - 'wallpapers' (Dict[str, str]): A dictionary mapping workspace names to their corresponding wallpaper paths.

    :return: None
    """
    xfconf_set("xsettings", "/Net/ThemeName", theme["gtk"])
    xfconf_set("xfwm4", "/general/theme", theme.get("xfwm", theme.get("gtk")))
    xfconf_set("xsettings", "/Net/IconThemeName", theme["icons"])
    xfconf_set("xsettings", "/Gtk/CursorThemeName", theme["cursor"])
    for workspace, wallpaper in theme["wallpapers"].items():
        xfconf_set("xfce4-desktop", workspace, wallpaper)


def get_wallpapers() -> dict[str, str]:
    """
    Returns a dictionary of wallpapers for each workspace.

    :return: A dictionary where each key is the workspace name and each value is the
             wallpaper path.
    :rtype: dict[str, str]
    """
    properties = get_properties("xfce4-desktop")
    workspaces = [p for p in properties if "/last-image" in p]
    wallpapers = {}
    for w in workspaces:
        wallpapers[w] = xfconf_get("xfce4-desktop", w)
    return wallpapers


def get_theme():
    return {
        "gtk": xfconf_get("xsettings", "/Net/ThemeName"),
        "xfwm": xfconf_get("xfwm4", "/general/theme"),
        "icons": xfconf_get("xsettings", "/Net/IconThemeName"),
        "cursor": xfconf_get("xsettings", "/Gtk/CursorThemeName"),
        "wallpapers": get_wallpapers(),
    }


def save(name: str):
    """
    Saves a theme with the given name to the configuration file.

    :param name: A string representing the name of the theme.
    :type name: str
    """
    config["themes"][name] = get_theme()
    config["enabled"] = name
    json.dump(config, open(CONFIG_PATH, "w"), indent=2)


def load(name: str):
    """
    Loads the theme with the given name if it is not currently loaded.

    :param name: The name of the theme to load.
    :type name: str
    """
    if config["enabled"] == name:
        notify(f'Already on "{name}" theme :)')
        return
    try:
        theme = config["themes"][name]
    except:
        notify(
            f'Theme "{name}" was not found in your config!',
            "script-error",
        )
        return
    notify(f'Loading "{name}" theme...')
    set_theme(theme)
    config["enabled"] = name
    json.dump(config, open(CONFIG_PATH, "w"), indent=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["load", "save", "auto", "toggle"])
    parser.add_argument("--name", required=False, help="Theme name")
    parser.add_argument(
        "--save-changes",
        required=False,
        type=bool,
        const=True,
        nargs='?',
        help="Save theme modifications before changing",
    )
    args = parser.parse_args()

    if args.action in ("load", "save") and args.name is None:
        notify("Theme name is missing.", "gnome-warning")
        return 1
    elif args.save_changes:
        tname = config["enabled"]
        save(tname)

    match args.action:
        case "auto":
            tzset()
            hour = localtime().tm_hour
            theme = "light" if hour > 6 and hour < 18 else "dark"
            load(theme)
        case "toggle":
            theme = "light" if config["enabled"] == "dark" else "dark"
            load(theme)
        case "save":
            save(args.name)
        case "load":
            load(args.name)

    return 0


if __name__ == "__main__":
    exit(main())
