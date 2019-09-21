#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Calendar-Indicator
#
# Copyright (C) 2011-2019 Lorenzo Carbonell Cerezo
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

import random
import os

def tohex():
    val = '%x'%random.randint(0, 16777215)
    if len(val[1:])<6:
        val = '#'+(6-len(val[1:]))*'0'+val[1:]
    return val

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def contraste(hexvalue):
    r,g,b = hex_to_rgb(hexvalue)
    a =1 - ( 0.299 * r + 0.587 * g + 0.114 * b)/255.
    if a < 0.5:
        d = 0
    else:
        d = 255
    return  rgb_to_hex((d,d,d))

def get_desktop_environment():
    desktop_session = os.environ.get("DESKTOP_SESSION")
    # easier to match if we doesn't have  to deal with caracter cases
    if desktop_session is not None:
        desktop_session = desktop_session.lower()
        if desktop_session in ["gnome", "unity", "cinnamon", "mate",
                               "budgie-desktop", "xfce4", "lxde", "fluxbox",
                               "blackbox", "openbox", "icewm", "jwm",
                               "afterstep", "trinity", "kde"]:
            return desktop_session
        # ## Special cases ##
        # Canonical sets $DESKTOP_SESSION to Lubuntu rather than
        # LXDE if using LXDE.
        # There is no guarantee that they will not do the same with
        # the other desktop environments.
        elif "xfce" in desktop_session or\
                desktop_session.startswith("xubuntu"):
            return "xfce4"
        elif desktop_session.startswith("ubuntu"):
            return "unity"
        elif desktop_session.startswith("lubuntu"):
            return "lxde"
        elif desktop_session.startswith("kubuntu"):
            return "kde"
        elif desktop_session.startswith("razor"):  # e.g. razorkwin
            return "razor-qt"
        elif desktop_session.startswith("wmaker"):  # eg. wmaker-common
            return "windowmaker"
    if os.environ.get('KDE_FULL_SESSION') == 'true':
        return "kde"
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        if "deprecated" not in os.environ.get(
                'GNOME_DESKTOP_SESSION_ID'):
            return "gnome2"
    # From http://ubuntuforums.org/showthread.php?t=652320
    elif is_running("xfce-mcs-manage"):
        return "xfce4"
    elif is_running("ksmserver"):
        return "kde"
    return "unknown"