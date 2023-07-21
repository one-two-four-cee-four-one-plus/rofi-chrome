#!/bin/sh
URL=$(rofi -dmenu -i -font "Iosevka Term 24" -window-title "goto" -theme-str "listview { enabled: false;}" 2>/dev/null)
if [ -z "$URL" ]; then
    exit 1
fi
curl -s -X "POST" -G "http://localhost:9222" --data-urlencode "url=$URL" --data-urlencode "goto=true"
