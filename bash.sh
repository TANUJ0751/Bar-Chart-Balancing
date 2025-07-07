#!/usr/bin/env bash

# Update and install dependencies
apt-get update && apt-get install -y wget gnupg unzip

# Add Google Chrome's official repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install Chrome
apt-get update && apt-get install -y google-chrome-stable
echo "Google Chrome installed successfully"


pip install -r requirements.txt