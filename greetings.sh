#!/usr/bin/env bash

name=$(whoami); name=${name^}
hour=$(date +%H)
icon=gnome-robots

greeting="Hello, Sr. $name!"
[[ $hour -gt 5 ]] && greeting="Good morning, Sr. $name!"
[[ $hour -gt 11 ]] && greeting="Good afternoon, Sr. $name!"
[[ $hour -gt 17 ]] && greeting="Good evening, Sr. $name!"

notify-send -i "$icon" "`echo -e $greeting`"
