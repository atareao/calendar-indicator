#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__="atareao"
__date__ ="$29-ene-2011$"
#
# com.py
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$24/09/2011'
__copyright__ = 'Copyright (c) 2011 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'
__version__ = '0.1.0.8.quantal.1'

import os
import locale
import gettext

######################################

def is_package():
	return not os.path.dirname(os.path.abspath(__file__)).endswith('src')

######################################

APP = 'calendar-indicator'
APPCONF = APP + '.conf'
CONFIG_DIR = os.path.join(os.path.expanduser('~'),'.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APPCONF)
BACKUP_FILE = os.path.join(CONFIG_APP_DIR, 'backup')
TOKEN_FILE = os.path.join(CONFIG_APP_DIR, 'token')
APPNAME = 'Calendar-Indicator'
if not os.path.exists(CONFIG_APP_DIR):
	os.makedirs(CONFIG_APP_DIR)

# check if running from source
if is_package():
	ROOTDIR = '/opt/extras.ubuntu.com/calendar-indicator/share/'
	LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
	APPDIR = os.path.join(ROOTDIR, APP)
	ICONDIR = os.path.join(APPDIR, 'icons')
	SOCIALDIR = os.path.join(APPDIR, 'social')
	CHANGELOG = os.path.join(APPDIR,'changelog')
else:
	ROOTDIR = os.path.dirname(__file__)
	LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../template1'))
	APPDIR = ROOTDIR
	DATADIR = os.path.normpath(os.path.join(ROOTDIR, '../data'))
	LOGOSDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/logos'))
	ICONDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/icons'))
	IMAGESDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/images'))
	SOCIALDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/social'))
	DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
	CHANGELOG = os.path.join(DEBIANDIR,'changelog')

f = open(CHANGELOG,'r')
line = f.readline()
f.close()
pos=line.find('(')
posf=line.find(')',pos)
VERSION = line[pos+1:posf].strip()
if not is_package():
	VERSION = VERSION + '-src'

ICON = os.path.join(ICONDIR,'calendar-indicator.svg')
ICON_NEW_EVENT = os.path.join(ICONDIR,'event-new.svg')
ICON_FINISHED_EVENT = os.path.join(ICONDIR,'event-finished.svg')

try:
	current_locale, encoding = locale.getdefaultlocale()
	language = gettext.translation(APP, LANGDIR, [current_locale])
	language.install()
	_ = language.gettext
except Exception as e:
	print(e)
	_ = str
