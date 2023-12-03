#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

rm -rf /opt/google-chrome-the-latest
rm -rf /usr/share/pixmaps/google-chrome-the-latest.png
rm -rf /usr/share/applications/google-chrome-the-latest.desktop
rm -rf /etc/cron.hourly/google-chrome-the-latest-cron.sh

