#!/usr/bin/env bash
# Automaticaly set CPU governor based on power supply


[[ "$(id -u)" != 0 ]] && echo "This script only runs as root" && exit 1

bat=/sys/class/power_supply/BAT1
charge="$(cat $bat/capacity)"

[[ "`< $bat/status`" = "Charging" ]]; charging=$?

if [ $charging == 0 ] || [ $charge -gt 65 ]; then
    governor=performance
elif [ $charge -gt 25 ]; then
    governor=conservative
else
    governor=powersave
fi

echo $governor | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
