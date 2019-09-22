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

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('Handy', '0.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Handy
import os
import shutil
import random
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from logindialog import LoginDialog
import comun
from comun import _
from utils import tohex, hex_to_rgb, rgb_to_hex, contraste
from sidewidget import SideWidget
from loginoption import LoginOption
from calendaroption import CalendarOption
from otheroption import OtherOption


class Preferences(Gtk.Dialog):
    def __init__(self,googlecalendar = None):
        self.googlecalendar = googlecalendar
        Gtk.Dialog.__init__(self)
        self.set_title(comun.APPNAME + ' | '+_('Preferences'))
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_size_request(1000, 400)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)

        mainbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        mainbox.set_border_width(5)
        self.get_content_area().add(mainbox)

        # Login, calendar, options

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_visible(True)
        scrolledwindow.set_size_request(200, 400)
        scrolledwindow.set_property('min-content-width', 200)
        mainbox.pack_start(scrolledwindow, False, False, 0)

        sidebar = Gtk.ListBox()
        sidebar.connect('row-activated', self.on_row_activated)
        scrolledwindow.add(sidebar)

        option1 = SideWidget(_('Google Calendar'),
                             'preferences-system-privacy-symbolic')
        sidebar.add(option1)
        option2 = SideWidget(_('Calendar options'),
                             'appointment-symbolic')
        sidebar.add(option2)
        option3 = SideWidget(_('General options'),
                             'preferences-system-symbolic')
        sidebar.add(option3)

        self.stack = Gtk.Stack()
        sw = Gtk.ScrolledWindow(child=self.stack)
        mainbox.pack_start(sw, True, True, 0)

        option1.set_stack('loginOption')

        self.loginOption = LoginOption()
        self.stack.add_named(self.loginOption, 'loginOption')

        option2.set_stack('calendarOption')
        self.calendarOption = CalendarOption(self.googlecalendar)
        self.stack.add_named(self.calendarOption, 'calendarOption')

        option3.set_stack('otherOption')
        self.otherOption = OtherOption()
        self.stack.add_named(self.otherOption, 'otherOption')

        self.center()

        self.show_all()

    def on_row_activated(self, lb, sidewidget):
        self.stack.set_visible_child_name(sidewidget.get_stack())
        if sidewidget.get_stack() == 'calendarOption':
            self.calendarOption.set_active()
        elif sidewidget.get_stack() == 'otherOption':
            self.otherOption.set_active()

    def center(self):
        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = self.get_preferred_width()[0]
        height = self.get_preferred_height()[0]
        self.move((monitor_width - width)/2, (monitor_height - height)/2)

if __name__ == "__main__":
    p = Preferences()
    if p.run() == Gtk.ResponseType.ACCEPT:
        p.save_preferences()
    p.destroy()
    exit(0)

