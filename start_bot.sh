#!/bin/bash
# Launch bot

cd "$(dirname "$0")/backend"
python3 -m src.bot_main
