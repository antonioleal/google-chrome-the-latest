#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#**********************************************************************************
#*                                                                                *
#*                             Google Chrome The Latest                           *
#*          ------------------------------------------------------------          *
#*                                                                                *
#**********************************************************************************
# Copyright 2023-2025 Antonio Leal, Porto Salvo, Portugal
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
DEB_FILE = 'google-chrome-stable_current_amd64.deb'
TXZ_FILE = DEB_FILE[:-3] + 'txz'
APP_PATH = '/opt/google-chrome-the-latest'
LASTRUN = APP_PATH + '/lastrun'
A_DAY_IN_SECONDS = 86400

MESSAGE_1 = """Hey, whatismybrowser.com reports a different Google Chrome version.

Whatismybrowser.com  : %s
Your current version : %s
Actual new version   : %s

Do you want to install it?
"""
MESSAGE_2 = """Chrome is now at version %s
Please review the installation output below:
"""
MESSAGE_3 = """Google Chrome versions listed at whatismybrowser.com vs available ones.

Whatismybrowser.com  : %s
Your current version : %s
Actual new version   : %s

You can now install it for the first time or, if
applicable, upgrade to the newest version.
"""
MESSAGE_4 = """Google Chrome versions is 'undetermined'
because it could not be read from whatismybrowser.com.

Do you want to continue all the same?
"""

command_permission = False
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
        global builder, command_permission
        window = builder.get_object("permission-dialog")        
        window.hide()
        Gtk.main_quit()
        command_permission = True
    def onButtonNoPressed(self, ButtonNo):
        global command_permission
        Gtk.main_quit()
        command_permission = False

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
def manual_dialog(web_version, installed_version, deb_version):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/manual-dialog.glade")
    builder.connect_signals(ManualHandler())
    window = builder.get_object("manual-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(MESSAGE_3 % (web_version, installed_version, deb_version))
    window.show_all()
    Gtk.main()

def permission_dialog(message):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/permission-dialog.glade")
    builder.connect_signals(PermissionHandler())
    window = builder.get_object("permission-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(message)
    window.show_all()
    Gtk.main()

def end_dialog(deb_version, log):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/end-dialog.glade")
    builder.connect_signals(EndHandler())
    window = builder.get_object("end-dialog")
    Log = builder.get_object("Label")
    Log.set_text(MESSAGE_2 % deb_version)
    Log = builder.get_object("Log")
    Log.get_buffer().set_text(log)
    window.show_all()
    Gtk.main()

def no_version_dialog():
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/no-version-dialog.glade")
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
def get_installed_version():
    if os.path.isfile('/usr/bin/google-chrome-stable'):
        try:
            installed_version = os.popen('google-chrome-stable --version').read().split()[2]
        except:
            installed_version = 'not found'
    else:
        installed_version = 'not found'
    return installed_version

# Download deb package from Google
def download_deb_package():
    os.chdir("SlackBuild")
    os.system('/usr/bin/wget %s/%s' % (DOWNLOAD_LINK, DEB_FILE))
    os.chdir("..")

# Get the version number from the deb file
def get_deb_version():
    os.chdir("SlackBuild")
    try:
        deb_version = os.popen('ar p ./google-chrome-stable_current_amd64.deb control.tar.xz | tar xJOf - ./control | grep Version | cut -d " " -f 2 | cut -d "-" -f 1').read().strip()
    except:
        deb_version = "not found"
    os.chdir("..")
    return deb_version

# Installing on your box
def install(deb_version):
    os.chdir("SlackBuild")
    log = "Installing Google Chrome " + str(deb_version)
    log = os.popen('chmod +x google-chrome-stable.SlackBuild').read()
    log = os.popen('./google-chrome-stable.SlackBuild').read()
    log += os.popen('/sbin/upgradepkg --install-new /tmp/google-chrome-stable-%s-x86_64-1.txz' % deb_version).read()
    #log += os.popen('cp /opt/google/chrome/product_logo_256.png /usr/share/pixmaps/google-chrome.png').read()
    os.chdir("..")
    return log

# remove rpm file
def delete_deb_package():
    os.chdir("SlackBuild")
    os.system('rm -rf %s*' % DEB_FILE)
    os.chdir("..")

#**********************************************************************************
#*                                                                                *
#                                Main Function                                    *
#*                                                                                *
#**********************************************************************************
def main():
    global command_permission, command_manual_install
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

    installed_version = str(get_installed_version()).strip()
    web_version = str(get_web_version()).strip()
    if web_version == "undetermined" and not param_silent:
        permission_dialog(MESSAGE_4)
        if not command_permission:
            exit(0)

    if param_show_gui:
        if installed_version != web_version:
            download_deb_package()
            deb_version = str(get_deb_version()).strip()
            if installed_version != deb_version:
                manual_dialog(web_version, installed_version, deb_version)
                if command_manual_install:
                    log = install(deb_version)
                    end_dialog(deb_version, log)
            else:
                no_version_dialog()
            delete_deb_package()
        else:
            no_version_dialog()
    else:
        if installed_version != web_version or param_install_or_upgrade:
            download_deb_package()
            deb_version = str(get_deb_version()).strip()
            if installed_version != deb_version:
                if not param_silent:
                    permission_dialog(MESSAGE_1 % (web_version, installed_version, deb_version))
                else:
                    command_permission = True
                if command_permission:
                    log = install(deb_version)
                    if not param_silent:
                        end_dialog(deb_version, log)
            delete_deb_package()

if __name__ == '__main__':
    main()

