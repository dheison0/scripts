#!/usr/bin/env bash

CONFIG_PATH="$HOME/.config/themes"
mkdir -p "$CONFIG_PATH" &>/dev/null

ACTION="$1"
OLD_NAME=$(cat "$CONFIG_PATH/enabled" 2>/dev/null)

GTK_THEME=
XFWM_THEME=
ICON_THEME=
CURSOR_THEME=
WALLPAPER=
IS_DARK=0
MONITOR=$(xfconf-query -c "xfce4-desktop" -l | grep '\-0/workspace0/last-image')

function notify() {
  echo "[THEME] $1"
  notify-send -i style "Theme Manager" "$1"
}

function get_config () {
  GTK_THEME=$(xfconf-query -c "xsettings" -p "/Net/ThemeName")
  XFWM_THEME=$(xfconf-query -c "xfwm4" -p "/general/theme")
  ICON_THEME=$(xfconf-query -c "xsettings" -p "/Net/IconThemeName")
  CURSOR_THEME=$(xfconf-query -c "xsettings" -p "/Gtk/CursorThemeName")
  WALLPAPER=$(xfconf-query -c "xfce4-desktop" -p "$MONITOR")
  if [ "$(gsettings get org.gnome.desktop.interface color-scheme)" = "'default'" ]; then
    IS_DARK=0
  else
    IS_DARK=1
  fi
}

function apply_config () {
  xfconf-query -c "xfwm4" -p "/general/theme" -s "$XFWM_THEME"
  xfconf-query -c "xsettings" -p "/Net/ThemeName" -s "$GTK_THEME"
  xfconf-query -c "xsettings" -p "/Net/IconThemeName" -s "$ICON_THEME"
  xfconf-query -c "xsettings" -p "/Gtk/CursorThemeName" -s "$CURSOR_THEME"
  xfconf-query -c "xfce4-desktop" -p "$MONITOR" -s "$WALLPAPER"
  if [ "$IS_DARK" = 1 ]; then
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' &>/dev/null
  else
    gsettings set org.gnome.desktop.interface color-scheme 'default' &>/dev/null
  fi
}

function load_config() {
  local file="$CONFIG_PATH/$1.sh"
  if [ -e "$file" ]; then
    source "$file"
  else
    echo "Theme not found: $1"
    return 2
  fi
}

function toggle() {
  notify "Switching theme..."
  if [ "$OLD_NAME" = "light" ]; then
    theme="dark"
  else
    theme="light"
  fi
  load_config "$theme"
  apply_config
  echo "$theme" > "$CONFIG_PATH/enabled"
}

function load() {
  [[ ! -n "$1" ]] && echo "You don't set theme name!" && exit 3
  notify "Loading $1 theme..."
  load_config "$1"
  apply_config
  echo "$1" > "$CONFIG_PATH/enabled"
}

function save() {
  if [ ! -n "$1" ]; then
    echo "Theme name not defined!"
    exit 2
  fi
  notify "Saving $1 theme..."
  get_config
  cat << EOF > "$CONFIG_PATH/$1.sh"
GTK_THEME='$GTK_THEME'
XFWM_THEME='$XFWM_THEME'
ICON_THEME='$ICON_THEME'
CURSOR_THEME='$CURSOR_THEME'
WALLPAPER='$WALLPAPER'
IS_DARK=$IS_DARK
EOF
}

HELP="usage: $(basename $0) action

Actions:
  load <name>     - Loads a saved theme
  save <name>     - Save actual state of XFCE as a theme
  toggle          - Switch between light and dark themes
  install-toggler - Install a menu item to switch between light and dark themes
  remove-toggler  - Remove theme toggler menu item"

case "$1" in 
  save) save "$2" "$3" ;;
  load) load "$2" ;;
  toggle) toggle ;;
  install-toggler)
  cp "$0" "$HOME/.local/theme.sh"
  cat << EOF > "$HOME/.local/share/applications/theme-toggler.desktop"
[Desktop Entry]
Name=Theme Switch
Comment=Switch between dark and light themes.
Exec=bash $HOME/.local/theme.sh toggle
Icon=style
Terminal=false
Type=Application
Categories=Settings;Appearance;
EOF
  ;;
  remove-toggler)
    rm "$HOME/.local/share/applications/theme-toggler.desktop" "$HOME/.local/theme.sh" 
    if [ $? = 0 ];then
      echo "Done."
    else
      echo "Fail!"
    fi
    ;;
  help) echo "$HELP"; exit 0 ;;
  *) echo "Unknown action: $1" && exit 1 ;;
esac
