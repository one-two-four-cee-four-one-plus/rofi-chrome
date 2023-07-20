#!/bin/sh
INDEX=$(curl -s 'http://localhost:9222' | rofi -dmenu -matching fuzzy -i -font "Iosevka Term 24" -window-title "close" 2>/dev/null | cut -d':' -f 1)
if [ -z "$INDEX" ]; then
    exit 0
fi
curl -X "DELETE" -G "http://localhost:9222" --data-urlencode "index=$INDEX"
