#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

DEST=/opt/google-chrome-the-latest
mkdir -p $DEST

cp google-chrome-the-latest.py* $DEST
cp -avxu dialogs $DEST
cp -avxu SlackBuild $DEST
cp uninstall.sh* $DEST
cp INSTALL $DEST
cp LICENSE $DEST
cp README $DEST

cp google-chrome-the-latest.png /usr/share/pixmaps
cp google-chrome-the-latest.desktop /usr/share/applications
cp google-chrome-the-latest-cron.sh /etc/cron.hourly

chown root:root /etc/cron.hourly/google-chrome-the-latest-cron.sh
chmod +x /etc/cron.hourly/google-chrome-the-latest-cron.sh

chown -R root:root $DEST
chmod -R 644 $DEST/*
chmod -R +x $DEST/*.py
chmod -R +x $DEST/*.sh
