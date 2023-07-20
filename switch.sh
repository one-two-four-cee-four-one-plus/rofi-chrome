#!/bin/sh
INDEX=$(curl -s 'http://localhost:9222' | rofi -dmenu -matching fuzzy -i -font "Iosevka Term 24" -window-title "switch" 2>/dev/null | cut -d':' -f 1)
if [ -z "$INDEX" ]; then
    exit 1
fi
curl -X "PUT" -G "http://localhost:9222" --data-urlencode "index=$INDEX"
