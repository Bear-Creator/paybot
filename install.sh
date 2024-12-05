#!bin/bash

sudo apt update && sudo apt upgrade 
if [ ! -d ./paybot ]; then
	git clone https://github.com/Bear-Creator/paybot
fi
cd ./paybot
git fetch origin

sudo apt install python3 python3-venv -y
sudo apt autoremove
python3 -m venv ./.venv
./.venv/bin/pip install -r ./install.txt

if [ ! -f ./config.py ]; then
	touch ./config.py
	read -p "Enter bots API token: " TOKEN
	read -p "Enter Admin's ID: " ADMIN
	reed -p "Enter payvment card nomber: " CARD
	printf "token = \"$TOKEN\"\nadmin = \"$ADMIN\"\ncard_number = $CARD" >> ./config.py
fi

sudo systemctl stop paybot.service
cp -i ./paybot.service /etc/systemd/system/
sudo systemctl restart paybot.service &
disown %%