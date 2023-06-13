#!/usr/bin/env python3
# Set xfce4 theme

from os import popen, environ
from sys import argv
from time import tzset, localtime
import json

CONFIG_PATH = environ.get('HOME', '.') + '/.config/themes.json'
try: themes = json.load(open(CONFIG_PATH))
except: themes = {}

class CommandFailed(Exception): pass

def xfconf_get_properties(channel: str) -> list[str]:
    cmd = f'xfconf-query -c "{channel}" -l'
    xfconf = popen(cmd)._proc
    if xfconf.wait() != 0:
        raise CommandFailed(f"{channel} is not a valid channel")
    output = xfconf.stdout.read()
    return output.strip().split()

def xfconf_get(channel: str, property_: str) -> str:
    cmd = f'xfconf-query -c "{channel}" -p "{property_}"'
    xfconf = popen(cmd)._proc
    if xfconf.wait() != 0:
        raise CommandFailed(f"xfconf-query command failed: {xfconf.stderr.read()}")
    output = xfconf.stdout.read()
    return output.strip()

def xfconf_set(channel: str, property_: str, value: str):
    cmd = f'xfconf-query -c "{channel}" -p "{property_}" -s "{value}"'
    xfconf = popen(cmd)._proc
    if xfconf.wait() != 0:
        raise CommandFailed(f"xfconf-query command failed: {xfconf.stderr.read()}")

def set_theme(theme: dict):
    xfconf_set('xsettings', '/Net/ThemeName', theme['gtk'])
    xfconf_set('xfwm4', '/general/theme', theme.get('xfwm', theme.get('gtk')))
    xfconf_set('xsettings', '/Net/IconThemeName', theme['icons'])
    xfconf_set('xsettings', '/Gtk/CursorThemeName', theme['cursor'])
    for w, wallpaper in theme['wallpapers'].items():
        xfconf_set('xfce4-desktop', w, wallpaper)

def get_wallpapers():
    properties = xfconf_get_properties('xfce4-desktop')
    workspaces = [p for p in properties if '/last-image' in p]
    wallpapers = {}
    for w in workspaces:
        wallpapers[w] = xfconf_get('xfce4-desktop', w)
    return wallpapers

def get_theme() -> dict:
    theme = {}
    theme['gtk'] = xfconf_get('xsettings', '/Net/ThemeName')
    theme['xfwm'] = xfconf_get('xfwm4', '/general/theme')
    theme['icons'] = xfconf_get('xsettings', '/Net/IconThemeName')
    theme['cursor'] = xfconf_get('xsettings', '/Gtk/CursorThemeName')
    theme['wallpapers'] = get_wallpapers()
    return theme

def save(name: str):
    themes[name] = get_theme()
    json.dump(themes, open(CONFIG_PATH, 'w'), indent=2)

def load(name: str):
    print(f'Loading theme {name}...')
    set_theme(themes[name])

if len(argv) < 2:
    print(f'usage: {argv[0]} load|save|autoselect [name]')
    exit(1)
elif argv[1] == 'autoselect':
    tzset()
    time = localtime()
    hour = time.tm_hour
    minute = time.tm_min
    if hour < 7 or hour >= 18:
        load('dark')
    else:
        load('light')
elif len(argv) > 3:
    print("Theme name missing.")
    exit(2)
elif argv[1] == 'load':
    load(argv[2])
elif argv[1] == 'save':
    save(argv[2])
