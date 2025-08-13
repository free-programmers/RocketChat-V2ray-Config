#!/bin/bash

# Variables
BOT_DIR="/var/rocketv2rayHunter"
SERVICE_NAME="v2ray-bot.service"
SYSTEMD_DIR="/etc/systemd/system"

# Check for root privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" 
    exit 1
fi

# Create the directory for the bot if it doesn't exist
mkdir -p $BOT_DIR

# Move the bot files to the proper location
echo "Moving bot files to $BOT_DIR..."
pip install -r requirements.txt
cp bot.py $BOT_DIR/
cp config.py $BOT_DIR/

# Create the systemd service file
echo "Creating systemd service..."

cat <<EOF > $SYSTEMD_DIR/$SERVICE_NAME
[Unit]
Description=RocketChat V2Ray Hunter
After=network.target

[Service]
ExecStart=/usr/bin/python3 $BOT_DIR/bot.py
WorkingDirectory=$BOT_DIR
User=root
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service
echo "Reloading systemd..."
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling the service to start on boot..."
systemctl enable $SERVICE_NAME

# Start the service
echo "Starting the service..."
systemctl start $SERVICE_NAME

# Check service status
echo "Service status:"
systemctl status $SERVICE_NAME

echo "Installation and setup complete!"
