#!/bin/sh
curl -s -X "GET" "http://localhost:9222/?url=true" | xclip -selection clipboard
