#!/usr/bin/env bash

# Output config
ACODEC=aac
VCODEC=h264
# Availably presets ordered by speed:
#  ultrafast > superfast > veryfast > faster > fast > medium > slow > slower > veryslow
PRESET=superfast
MAX_FPS=24

# Script configs
LOCK_FILE=/tmp/converter.lock
PID_FILE=/tmp/converter.pid
QUEUE=$HOME/.convert_queue
ERRORS=$HOME/.convert_errors
MAX_THREADS=$((2 * 12))
SEPARATOR=" <|> "

[[ ! -e "$QUEUE" ]] && touch "$QUEUE"

function quit() {
  echo "[QUIT] $1"
  exit $2
}

function info() {
  echo "[INFO] $@"
}

function cli() {
  case "$1" in
  add)
    while [ -e "$LOCK_FILE" ]; do sleep 1; done
    local input=$(realpath "$2")
    local output=$(realpath "$3")
    echo "$input${SEPARATOR}$output" >>"$QUEUE"
    echo "Added to queue!"
    ;;
  list)
    cat "$QUEUE" | while read item; do
      echo "${item//${SEPARATOR}*/} → ${item//*${SEPARATOR}/}"
    done
    ;;
  *)
    cat <<EOF
usage: convert cli [action] [options...]
Actions:
  add - Add a new item to queue
    1. Input location
    2. Output location
  list - List actual queue
EOF
    ;;
  esac
}

function daemon() {
  if [ -e "$PID_FILE" ]; then
    if [ "$1" == "-f" ] || [ "$1" == "--force" ]; then
      kill $(<"$PID_FILE")
      rm -rf "$PID_FILE" "$LOCK_FILE"
    else
      quit "Daemon already started!"
    fi
  fi
  echo "$$" >"$PID_FILE"
  info "Daemon started, waiting..."
  (
    while [ -e "$PID_FILE" ]; do
      sleep 1
      local item="$(head -1 "$QUEUE")"
      [[ ! -n "$(<"$QUEUE")" ]] && continue

      local input="${item//${SEPARATOR}*/}"
      local output="${item//*${SEPARATOR}/}"
      info "Processing item '$input'..."
      ffmpeg -hide_banner -y \
        -loglevel error \
        -threads $MAX_THREADS \
        -i "${input}" \
        -c:v $VCODEC -c:a $ACODEC \
        -fpsmax $MAX_FPS \
        -preset superfast \
        "${output}"
      [[ $? != 0 ]] && (
        info "Failed to convert!"
        echo "$item" >>"$ERRORS"
      ) || info "Converted!"

      touch "$LOCK_FILE"
      local lines=$(wc -l <"$QUEUE")
      tail --lines=$(($lines - 1)) "$QUEUE" | tee "$QUEUE" >/dev/null
      rm -rf "$LOCK_FILE"
    done
  ) &
  function killed() {
    rm -rf "$PID_FILE" "$LOCK_FILE"
    quit "Daemon killed!" 127
  }
  trap killed SIGINT
  wait
}

case "$1" in
cli)
  shift
  cli "$1" "$2" "$3"
  ;;
daemon)
  shift
  daemon "$1"
  ;;
*) quit "usage: converter [cli|daemon] [options...]" 1 ;;
esac
