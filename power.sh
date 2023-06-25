#!/usr/bin/env bash

# Automaticaly set CPU governor based on power supply
# > If the system is charging the governor will always be "performance"
#   otherwise if battery is gran than 85% it will be "performance" too
#   but if it's 35% or upper it will be "conservative" and if lower it
#   will be "powersave"

[[ "$(id -u)" != 0 ]] && echo "This script only runs as root" && exit 1

bat=/sys/class/power_supply/BAT1
charge="$(cat $bat/capacity)"

[[ "`< $bat/status`" = "Charging" ]]; charging=$?

if [ $charging == 0 ] || [ $charge -gt 85 ]; then
    governor=performance
elif [ $charge -gt 35 ]; then
    governor=conservative
else
    governor=powersave
fi

echo $governor | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
