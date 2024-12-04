#!bin/sh

sudo apt update && sudo apt upgrade 
mkdir -p ~/paybot
cd ~/paybot

sudo apt install python3-venv -y
python3 -m venv ./.venv
./.venv/bin/pip install -r ./install.txt

if [ ! -f ./config.py ]; then
	touch ./config.py
	read -p "Enter bots API token: " TOKEN
	read -p "Enter Admin's ID: " ADMIN
	printf "token = \"$TOKEN\"\nadmin = \"$ADMIN\"" >> ./config.py
fi

cp ./paybot.service /etc/systemd/system/
sudo systemctl restart paybot.service &
disown %%