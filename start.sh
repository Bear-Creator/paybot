#!/bin/bash

if [ ! -f ./config.py ]; then
        touch ./config.py
        printf "token = \"YOUR_API_TOKEN\"\nadmin = \"ADMIN_ID\"" >> ./config.py
fi
/.venv/bin/python ./bot.py

