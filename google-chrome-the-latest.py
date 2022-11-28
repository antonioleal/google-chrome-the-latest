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
import tkinter as tk
from tkinter import messagebox

DOWNLOAD_LINK = 'https://dl.google.com/linux/direct'
DOWNLOAD_FILE = 'google-chrome-stable_current_x86_64.rpm'
TXZ_FILE = DOWNLOAD_FILE[:-3] + 'txz'
LASTRUN = '/opt/google-chrome-the-latest/lastrun'

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

# Only run once a day, even though we set cron.hourly
if os.path.exists(LASTRUN) and not upgrade_install:
    ti_m = os.path.getmtime(LASTRUN)
    ti_n = time.time()
    if (ti_n - ti_m) < 86400:
        exit(0)
os.system('touch %s' % LASTRUN)

# Check the web for latest Chrome version.
# We are expecting sometning like:
# xmlstr = """
# <tr>
    # <td>Chrome on <strong>Linux</strong></td>
    # <td>107.0.5304.121</td>
    # <td>2022-11-25</td>
# </tr>
# """
xmlstr=os.popen('curl -s https://www.whatismybrowser.com/guides/the-latest-version/chrome | grep -B 1 -A 3 "<td>Chrome on <strong>Linux</strong></td>"').read()
root = ET.fromstring(xmlstr)
latest_version = root[1].text.strip()

# Check the current installed version, if there is one...
try:
    current_version = os.popen('google-chrome-stable --version').read().split()[2]
except:
    current_version = 'not found'

# Do upgrade or install
if current_version != latest_version or upgrade_install:
    # Download from google and confirm the release version
    os.chdir('/tmp')
    os.system('rm -rf %s %s' % (DOWNLOAD_FILE, TXZ_FILE))
    os.system('/usr/bin/wget %s/%s' % (DOWNLOAD_LINK, DOWNLOAD_FILE))
    actual_version = os.popen("rpm -q google-chrome-stable_current_x86_64.rpm | grep '^google' | awk -F - '{ print $4 }'").read().strip()
    # Proceed if a new version is actually confirmed
    if current_version != actual_version or upgrade_install:
        INSTALL_FILE = 'google-chrome-stable-%s-x86_64-1.txz' % actual_version
        if not silent:
            dialog = tk.Tk()
            dialog.withdraw()
            msg = """Hey, there is a new Google Chrome release!

Your version: %s
New version : %s

Do you want to install it?""" % (current_version, actual_version)    
            yesno = messagebox.askyesno(title='Chrome, the latest', message=msg)
            dialog.destroy()
        else:
            yesno = True
        if yesno:
            os.system('/usr/bin/rpm2txz %s' % DOWNLOAD_FILE)
            os.system('mv %s %s' % (TXZ_FILE, INSTALL_FILE))
            os.system('/sbin/upgradepkg --install-new %s' % INSTALL_FILE)
            os.system('rm -rf %s %s ' % (DOWNLOAD_FILE, INSTALL_FILE))

            if not silent:
                dialog = tk.Tk()
                dialog.withdraw()
                messagebox.showinfo("Done","Google Chrome is now at version %s" % actual_version)
