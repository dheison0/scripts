#!/usr/bin/env bash

set -e

v="$(ddcutil --display 1 getvcp 10)" # Get information about display brightness
v="${v// /}"; v="${v//,*/}"; v="${v//*=/}" # Filter for current value only

ACTUAL_VALUE=$v
INPUT_VALUE=${2:-10}
NEW_VALUE=$ACTUAL_VALUE

case "$1" in
	+|i) NEW_VALUE=$[$ACTUAL_VALUE+$INPUT_VALUE];;
	-|d) NEW_VALUE=$[$ACTUAL_VALUE-$INPUT_VALUE];;
	*) echo "usage: $0 <+|-> <value>" && exit 1;;
esac

[[ $NEW_VALUE -lt 0 ]] && NEW_VALUE=0
[[ $NEW_VALUE -gt 100 ]] && NEW_VALUE=100

[[ $NEW_VALUE != $ACTUAL_VALUE ]] && ddcutil --display 1 setvcp 10 $NEW_VALUE

notify-send \
	-r 999 \
	-i "video-display-brightness-symbolic" \
	-h "int:value:$NEW_VALUE" \
	"Brightness" "${NEW_VALUE}%" 
