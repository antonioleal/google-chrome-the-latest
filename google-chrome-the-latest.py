#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#**********************************************************************************
#*                                                                                *
#*                             Google Chrome The Latest                           *
#*          ------------------------------------------------------------          *
#*                                                                                *
#**********************************************************************************
# Copyright 2024 Antonio Leal, Porto Salvo, Portugal
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


#**********************************************************************************
#*                                                                                *
#*                                    Libraries                                   *
#*                                                                                *
#**********************************************************************************
import os
import time
import sys
import xml.etree.ElementTree as ET
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

#**********************************************************************************
#*                                                                                *
# Globals                                                                         *
#*                                                                                *
#**********************************************************************************
# Program variables
DOWNLOAD_LINK = 'https://dl.google.com/linux/direct'
RPM_FILE = 'google-chrome-stable_current_x86_64.rpm'
TXZ_FILE = RPM_FILE[:-3] + 'txz'
APP_PATH = '/opt/google-chrome-the-latest'
LASTRUN = APP_PATH + '/lastrun'
A_DAY_IN_SECONDS = 86400

MESSAGE_1 = """Hey, whatismybrowser.com reported a new Google Chrome.

Your version : %s
New version  : %s

Do you want to install it?
"""
MESSAGE_2 = """Chrome is now at version %s
Please review the installation output below:
"""
MESSAGE_3 = """Google Chrome versions available.

Your version   : %s
Latest version : %s

You can now install it for the first time or, if
applicable, upgrade to the newest version.
"""
command_confirm_upgrade = False
command_manual_install = False
builder = None

#**********************************************************************************
#*                                                                                *
#                                  Gui Handlers                                   *
#*                                                                                *
#**********************************************************************************
class ManualHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonInstallPressed(self, ButtonInstall):
        global builder, command_manual_install
        window = builder.get_object("manual-dialog")
        window.hide()
        Gtk.main_quit()
        command_manual_install = True
    def onButtonQuitPressed(self, ButtonQuit):
        Gtk.main_quit()

class PermissionHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonYesPressed(self, ButtonYes):
        global builder, command_confirm_upgrade
        window = builder.get_object("permission-dialog")        
        window.hide()
        Gtk.main_quit()
        command_confirm_upgrade = True
    def onButtonNoPressed(self, ButtonNo):
        global command_confirm_upgrade
        Gtk.main_quit()
        command_confirm_upgrade = False

class EndHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonOKPressed(self, ButtonOK):
        Gtk.main_quit()

class NoVersionHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonDonePressed(self, ButtonDone):
        Gtk.main_quit()

#**********************************************************************************
#*                                                                                *
#                                    Dialogs                                      *
#*                                                                                *
#**********************************************************************************
def manual_dialog(current_version, new_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("manual-dialog.glade")
    builder.connect_signals(ManualHandler())
    window = builder.get_object("manual-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_3 % (current_version, new_version))
    window.show_all()
    Gtk.main()

def permission_dialog(current_version, new_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("permission-dialog.glade")
    builder.connect_signals(PermissionHandler())
    window = builder.get_object("permission-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_1 % (current_version, new_version))
    window.show_all()
    Gtk.main()

def end_dialog(new_version, log):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("end-dialog.glade")
    builder.connect_signals(EndHandler())
    window = builder.get_object("end-dialog")
    Log = builder.get_object("Label")
    Log.set_text(MESSAGE_2 % new_version)
    Log = builder.get_object("Log")
    Log.get_buffer().set_text(log)
    window.show_all()
    Gtk.main()

def no_version_dialog():
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("no-version-dialog.glade")
    builder.connect_signals(NoVersionHandler())
    window = builder.get_object("no-version-dialog")
    window.show_all()
    Gtk.main()

#**********************************************************************************
#*                                                                                *
#                               Core functions                                    *
#*                                                                                *
#**********************************************************************************
# Check the web for latest Chrome version.
def get_web_version():
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
        web_version = root[1].text.strip()
    except:
        web_version = 'undetermined'
    return web_version
    
# Check the current installed version, if there is one...
def get_current_version():
    if os.path.isfile('/usr/bin/google-chrome-stable'):
        try:
            current_version = os.popen('google-chrome-stable --version').read().split()[2]
        except:
            current_version = 'not found'
    else:
        current_version = 'not found'
    return current_version

# Download from google and confirm the release version
def get_new_version():
    os.system('/usr/bin/wget %s/%s' % (DOWNLOAD_LINK, RPM_FILE))
    return os.popen("rpm -q google-chrome-stable_current_x86_64.rpm | grep '^google' | awk -F - '{ print $4 }'").read().strip()

# Installing on you box
def install(new_version):
    INSTALL_FILE = 'google-chrome-stable-%s-x86_64-1.txz' % new_version
    log = os.popen('/usr/bin/rpm2txz %s' % RPM_FILE).read()
    log += os.popen('mv %s %s' % (TXZ_FILE, INSTALL_FILE)).read()
    log += os.popen('/sbin/upgradepkg --install-new %s' % INSTALL_FILE).read()
    log += os.popen('mv %s /tmp' % INSTALL_FILE).read()
    log += os.popen('cp /opt/google/chrome/product_logo_256.png /usr/share/pixmaps/google-chrome.png').read()
    return log

# remove rpm file
def remove_rpm_file():
    os.system('rm -rf %s' % RPM_FILE)

#**********************************************************************************
#*                                                                                *
#                                Main Function                                    *
#*                                                                                *
#**********************************************************************************
def main():
    global command_confirm_upgrade, command_manual_install
    os.chdir(APP_PATH)

    # Check if you are root
    if os.geteuid() != 0:
        print('You must run this script as root.')
        exit(0)
    
    # Read program arguments
    param_silent = False
    param_install_or_upgrade = False
    param_show_gui = False
    for a in sys.argv:
        if 'GUI' == a.upper():
            param_show_gui = True
        if 'INSTALL' == a.upper() or 'UPGRADE' == a.upper() or 'UPDATE' == a.upper():
            param_install_or_upgrade = True
        if 'SILENT' == a.upper():
            param_silent = True

    # Exit if $DISPLAY is not set
    if len(os.popen("echo $DISPLAY").read().strip()) == 0 and not param_silent:
        print('In order to run you must have an XServer running, otherwise use the "silent" program argument.')
        exit(0)

    # Only run once a day, even though we set cron.hourly
    if os.path.exists(LASTRUN) and not (param_install_or_upgrade or param_show_gui):
        ti_m = os.path.getmtime(LASTRUN)
        ti_n = time.time()
        if (ti_n - ti_m) < A_DAY_IN_SECONDS:
            exit(0)
    os.system('touch %s' % LASTRUN)

    # Core processing
    current_version = get_current_version()
    if param_show_gui:
        new_version = get_new_version()
        if current_version != new_version:
            manual_dialog(current_version, new_version)
            if command_manual_install:
                log = install(new_version)
                end_dialog(new_version, log)
        else:
            no_version_dialog()
        remove_rpm_file()
    else:
        web_version = get_web_version()
        if current_version != web_version or param_install_or_upgrade:
            new_version = get_new_version()
            if current_version != new_version or param_install_or_upgrade:
                if not param_silent:
                    permission_dialog(current_version, new_version)
                else:
                    command_confirm_upgrade = True
                if command_confirm_upgrade:
                    log = install(new_version)
                    if not param_silent:
                        end_dialog(new_version, log)
            remove_rpm_file()

if __name__ == '__main__':
    main()
