#!/usr/bin/env bash

CONFIG_PATH="$HOME/.config/themes"
mkdir -p "$CONFIG_PATH" &>/dev/null

ACTION="$1"
NAME="$2"
OLD_NAME=$(cat "$CONFIG_PATH/enabled" 2>/dev/null)

GTK_THEME=
XFWM_THEME=
ICON_THEME=
CURSOR_THEME=
WALLPAPER=

function notify() {
  echo "[THEME] $1"
  notify-send -i style "Theme Manager" "$1"
}

function get_config () {
  GTK_THEME=$(xfconf-query -c "xsettings" -p "/Net/ThemeName")
  XFWM_THEME=$(xfconf-query -c "xfwm4" -p "/general/theme")
  ICON_THEME=$(xfconf-query -c "xsettings" -p "/Net/IconThemeName")
  CURSOR_THEME=$(xfconf-query -c "xsettings" -p "/Gtk/CursorThemeName")
  WALLPAPER=$(xfconf-query -c "xfce4-desktop" -p "/backdrop/screen0/monitor0/last-image")
}

function set_config () {
  xfconf-query -c "xsettings" -p "/Net/ThemeName" -s "$GTK_THEME"
  xfconf-query -c "xfwm4" -p "/general/theme" -s "$XFWM_THEME"
  xfconf-query -c "xsettings" -p "/Net/IconThemeName" -s "$ICON_THEME"
  xfconf-query -c "xsettings" -p "/Gtk/CursorThemeName" -s "$CURSOR_THEME"
  xfconf-query -c "xfce4-desktop" -p "/backdrop/screen0/monitor0/last-image" -s "$WALLPAPER"
  echo "$NAME" > "$CONFIG_PATH/enabled"
}

function load_config() {
  local file="$CONFIG_PATH/$NAME.sh"
  if [ -e "$file" ]; then
    source "$file"
  else
    echo "Theme not found: $NAME"
    return 2
  fi
}

function toggle() {
  notify "Switching theme..."
  if [ "$OLD_NAME" = "light" ]; then
    NAME="dark"
  else
    NAME="light"
  fi
  load_config
  set_config
}

function load() {
  [[ ! -n "$NAME" ]] && echo "You don't set theme name!" && exit 3
  notify "Loading $NAME theme..."
  load_config
  set_config
}

function save() {
  if [ ! -n "$NAME" ]; then
    echo "Theme name not defined!"
    exit 2
  fi
  notify "Saving $NAME theme..."
  get_config
  cat << EOF > "$CONFIG_PATH/$NAME.sh"
GTK_THEME='$GTK_THEME'
XFWM_THEME='$XFWM_THEME'
ICON_THEME='$ICON_THEME'
CURSOR_THEME='$CURSOR_THEME'
WALLPAPER='$WALLPAPER'
EOF
}

HELP="usage: $(basename $0) action [name]

Actions:
  load - Loads a saved theme
  save - Save actual state of XFCE as a theme
  toggle - Switch between light and dark themes

Optional parameters:
  name - Name of theme to load/saved"

case "$1" in 
  load|save|toggle) eval "$1"; exit $? ;;
  help) echo "$HELP"; exit 0 ;;
  *) echo "Unknown action: $1" && exit 1 ;;
esac
