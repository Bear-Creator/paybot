#!/bin/bash

if [ ! -f ./config.py ]; then
        touch ./config.py
        printf "token = \"YOUR_API_TOKEN\"\nadmin = \"ADMIN_ID\"\ncard_number = 0000 0000 0000 0000"" >> ./config.py
fi
/.venv/bin/python ./bot.py

