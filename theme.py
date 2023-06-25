#!/usr/bin/env python3
# Utility to set XFCE theme

from os import environ
from time import localtime, tzset
import subprocess, json, argparse


CONFIG_PATH = environ.get('HOME', '/root') + '/.config/themes.json'
try: config = json.load(open(CONFIG_PATH))
except: config = {'themes': {}, 'enabled': ''}


class CommandFailed(Exception): pass

def notify(title: str, message: str):
    subprocess.run(['notify-send', '-i', 'style', title, message])


def get_properties(channel: str) -> list:
    """
    Retrieves a list of properties from the specified channel using the xfconf-query command.

    :param channel: a string representing the channel to retrieve properties from
    :type channel: str
    :return: a list of properties retrieved from the specified channel
    :rtype: list
    :raises ValueError: if the specified channel is not a valid channel
    """
    command = ['xfconf-query', '-c', channel, '-l']
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise ValueError(f"{channel} is not a valid channel")
    output = process.stdout.decode().strip()
    return output.split('\n')


def xfconf_get(channel: str, property_name: str) -> str:
    """
    This function retrieves the value of a property from the given XFCE channel using the `xfconf-query` command.
    
    :param channel: A string representing the XFCE channel to retrieve the property value from.
    :param property_name: A string representing the name of the property to retrieve the value of.
    :return: A string representing the value of the property.
    :raises: CommandFailed, if the `xfconf-query` command fails to execute.
    """
    cmd = f'xfconf-query -c "{channel}" -p "{property_name}"'
    xfconf = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if xfconf.returncode != 0:
        raise CommandFailed(f"xfconf-query command failed: {xfconf.stderr.decode()}")
    output = xfconf.stdout.decode()
    return output.strip()


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
    command = f'xfconf-query -c "{channel}" -p "{property_name}" -s "{value}"'
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if process.returncode != 0:
        raise CommandFailed(f"xfconf-query command failed: {process.stderr.decode().strip()}")


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
    xfconf_set('xsettings', '/Net/ThemeName', theme['gtk'])
    xfconf_set('xfwm4', '/general/theme', theme.get('xfwm', theme.get('gtk')))
    xfconf_set('xsettings', '/Net/IconThemeName', theme['icons'])
    xfconf_set('xsettings', '/Gtk/CursorThemeName', theme['cursor'])
    for w, wallpaper in theme['wallpapers'].items():
        xfconf_set('xfce4-desktop', w, wallpaper)


def get_wallpapers() -> dict[str, str]:
    """
    Returns a dictionary of wallpapers for each workspace.
    
    :return: A dictionary where each key is the workspace name and each value is the 
             wallpaper path.
    :rtype: dict[str, str]
    """
    properties = get_properties('xfce4-desktop')
    workspaces = [p for p in properties if '/last-image' in p]
    wallpapers = {}
    for w in workspaces:
        wallpapers[w] = xfconf_get('xfce4-desktop', w)
    return wallpapers


get_theme = lambda: {
    'gtk': xfconf_get('xsettings', '/Net/ThemeName'),
    'xfwm': xfconf_get('xfwm4', '/general/theme'),
    'icons': xfconf_get('xsettings', '/Net/IconThemeName'),
    'cursor': xfconf_get('xsettings', '/Gtk/CursorThemeName'),
    'wallpapers': get_wallpapers()
}


def save(name: str):
    """
    Saves a theme with the given name to the configuration file.
    
    :param name: A string representing the name of the theme.
    :type name: str
    """
    config['themes'][name] = get_theme()
    json.dump(config, open(CONFIG_PATH, 'w'), indent=2)


def load(name: str):
    """
    Loads the theme with the given name if it is not currently loaded. 

    :param name: The name of the theme to load.
    :type name: str
    """
    if config['enabled'] == name:
        return
    notify('Changing theme', f'Loading "{name}" theme...')
    set_theme(config['themes'][name])
    config['enabled'] = name
    json.dump(config, open(CONFIG_PATH, 'w'), indent=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['load', 'save', 'auto'])
    parser.add_argument('--name', required=False)
    args = parser.parse_args()
    
    if args.action in ('load', 'save') and args.name is None:
        print("Theme name is missing.")
        return 1

    match args.action:
        case 'auto':
            tzset()
            hour = localtime().tm_hour
            theme = 'light' if hour > 6 and hour < 19 else 'dark'
            load(theme)
        case 'save': save(args.name)
        case 'load': load(args.name)
    
    return 0


exit(main())
