#!/bin/bash

DEST=/opt/google-chrome-the-latest
mkdir -p $DEST
chmod +x google-chrome-the-latest.py
chmod +x google-chrome-the-latest-cron.sh

cp google-chrome-the-latest.py $DEST
cp google-chrome-the-latest-cron.sh $DEST
cp permission-dialog.glade $DEST
cp end-dialog.glade $DEST
cp google-chrome-the-latest.png $DEST
cp whatismybrowser-logo.png $DEST
cp README $DEST
cp INSTALL $DEST
cp LICENSE $DEST

cp google-chrome-the-latest-cron.sh /etc/cron.hourly
