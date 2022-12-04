#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#**********************************************************************************
#*                                                                                *
#*                             Google Chrome The Latest                           *
#*          ------------------------------------------------------------          *
#*                                                                                *
#**********************************************************************************
# Copyright 2022 Antonio Leal, Porto Salvo, Portugal
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Id:$

import os
import time
import sys
import xml.etree.ElementTree as ET
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Program variables
DOWNLOAD_LINK = 'https://dl.google.com/linux/direct'
RPM_FILE = 'google-chrome-stable_current_x86_64.rpm'
TXZ_FILE = RPM_FILE[:-3] + 'txz'
APP_PATH = '/opt/google-chrome-the-latest'
LASTRUN = APP_PATH + '/lastrun'
A_DAY_IN_SECONDS = 86400
MESSAGE_1 = """Hey, whatismybrowser.com reported a new Google Chrome version: %s

Your version   : %s
Actual version : %s

Do you want to install it?
"""
MESSAGE_2 = """Chrome is now at version %s
Please review the installation output below:
"""
yesno = False
builder = None

class PermissionHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonYesPressed(self, ButtonYes):
        global yesno, builder
        window = builder.get_object("permission-dialog")        
        window.hide()
        Gtk.main_quit()
        yesno = True
    def onButtonNoPressed(self, ButtonNo):
        global yesno    
        Gtk.main_quit()
        yesno = False

class EndHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonOKPressed(self, ButtonOK):
        Gtk.main_quit()

# Check the web for latest Chrome version.
def get_latest_version():
    try:
        # We are expecting sometning like:
        # xmlstr = """
        # <tr>
            # <td>Chrome on <strong>Linux</strong></td>
            # <td>108.0.5359.94</td>
            # <td>2022-11-25</td>
        # </tr>
        # """
        xmlstr=os.popen('curl -s https://www.whatismybrowser.com/guides/the-latest-version/chrome | grep -B 1 -A 3 "<td>Chrome on <strong>Linux</strong></td>"').read()
        root = ET.fromstring(xmlstr)
        latest_version = root[1].text.strip()
    except:
        latest_version = 'undetermined'
    return latest_version
    
# Check the current installed version, if there is one...
def get_current_version():
    try:
        current_version = os.popen('google-chrome-stable --version').read().split()[2]
    except:
        current_version = 'not found'
    return current_version

# Download from google and confirm the release version
def get_actual_version():
    os.chdir(APP_PATH)
    os.system('rm -rf %s %s' % (RPM_FILE, TXZ_FILE))
    os.system('/usr/bin/wget %s/%s' % (DOWNLOAD_LINK, RPM_FILE))
    return os.popen("rpm -q google-chrome-stable_current_x86_64.rpm | grep '^google' | awk -F - '{ print $4 }'").read().strip()

def ask_permission_to_install(latest_version, current_version, actual_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("permission-dialog.glade")
    builder.connect_signals(PermissionHandler())
    window = builder.get_object("permission-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_1 % (latest_version, current_version, actual_version))
    window.show_all()
    Gtk.main()

def install(actual_version):
    INSTALL_FILE = 'google-chrome-stable-%s-x86_64-1.txz' % actual_version
    log = os.popen('/usr/bin/rpm2txz %s' % RPM_FILE).read()
    log += os.popen('mv %s %s' % (TXZ_FILE, INSTALL_FILE)).read()
    log += os.popen('/sbin/upgradepkg --install-new %s' % INSTALL_FILE).read()
    log += os.popen('rm -rf %s %s ' % (RPM_FILE, INSTALL_FILE)).read()
    return log

def end_dialog(actual_version, log):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("end-dialog.glade")
    builder.connect_signals(EndHandler())
    window = builder.get_object("end-dialog")
    Log = builder.get_object("Label")
    Log.set_text(MESSAGE_2 % actual_version)
    Log = builder.get_object("Log")
    Log.get_buffer().set_text(log)
    window.show_all()
    Gtk.main()

  
def main():
    global yesno
    # Check if you are root
    if os.geteuid() != 0:
        print('You must run this script as root.')
        exit(0)
    
    # Read program arguments
    silent = False
    upgrade_install = False
    for a in sys.argv:
        if 'SILENT' == a.upper(): silent = True
        if 'INSTALL' == a.upper(): upgrade_install = True
        if 'UPGRADE' == a.upper(): upgrade_install = True

    # Exit if $DISPLAY is not set
    if len(os.popen("echo $DISPLAY").read().strip()) == 0 and not silent:
        print('In order to run you must have an XServer running, otherwise use the "silent" program argument.')
        exit(0)

    # Only run once a day, even though we set cron.hourly
    if os.path.exists(LASTRUN) and not upgrade_install:
        ti_m = os.path.getmtime(LASTRUN)
        ti_n = time.time()
        if (ti_n - ti_m) < A_DAY_IN_SECONDS:
            exit(0)
    os.system('touch %s' % LASTRUN)

    latest_version = get_latest_version()
    current_version = get_current_version()

    if current_version != latest_version or upgrade_install:
        actual_version = get_actual_version()
        if current_version != actual_version or upgrade_install:
            if not silent:
                ask_permission_to_install(latest_version, current_version, actual_version)
            else:
                yesno = True
            if yesno:
                log = install(actual_version)
                if not silent:
                    end_dialog(actual_version, log)

if __name__ == '__main__':
    main()
