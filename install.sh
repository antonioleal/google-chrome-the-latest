#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

DEST=/opt/google-chrome-the-latest
mkdir -p $DEST

chmod 644 *
chmod +x *.py
chmod +x *.sh

cp * $DEST

cp google-chrome-the-latest.png /usr/share/pixmaps
cp google-chrome-the-latest.desktop /usr/share/applications
cp google-chrome-the-latest-cron.sh /etc/cron.hourly
