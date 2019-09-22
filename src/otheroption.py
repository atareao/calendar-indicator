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
    gi.require_version('Handy', '0.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Handy
import os
import urllib
import comun
import shutil
from comun import _
from sidewidget import SideWidget
from settingsrow import SettingRow
from settingsspinrow import SettingSpinRow
from configurator import Configuration

class OtherOption(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.__set_ui()

    def __set_ui(self):
        handycolumn = Handy.Column()
        handycolumn.set_maximum_width(700)
        handycolumn.set_margin_top(24)
        self.add(handycolumn)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        handycolumn.add(box)

        label = Gtk.Label(_('Options'))
        label.set_name('special')
        label.set_alignment(0, 0.5)
        box.add(label)

        listbox0 = Gtk.ListBox()
        box.add(listbox0)

        self.options = {}
        for option in ['autostart', 'theme']:
            self.options[option] = Gtk.Switch()
            self.options[option].set_valign(Gtk.Align.CENTER)
        self.options['theme'].connect('button-press-event',self.on_options_changed)
        self.options['theme'].connect('activate',self.on_options_changed)

        self.options['time'] = Gtk.SpinButton()
        self.options['time'].set_range(2,24)
        self.options['time'].set_increments(2,4)

        listbox0.add(SettingSpinRow(_('Time between automatic syncronizations (hours)'),
                        _('Time between automatic syncronizations (hours)'),
                        self.options['time']))
        self.options['time'].connect('button-press-event',self.on_options_changed)
        self.options['time'].connect('activate',self.on_options_changed)


        listbox0.add(SettingRow(_('Autostart'),
                        _('Init Calendar Indicator with the operating system.'),
                        self.options['autostart']))
        self.options['autostart'].connect('button-press-event',self.on_options_autostart_changed)
        self.options['autostart'].connect('activate',self.on_options_autostart_changed)


        listbox0.add(SettingRow(_('Theme light'),
                        _('Would theme for Calendar Indicator icons do you prefer?'),
                        self.options['theme']))

    def set_active(self):
        configuration = Configuration()
        self.options['time'].set_value(configuration.get('time'))
        self.options['theme'].set_active(configuration.get('theme') == 'light')
        filestart = os.path.join(
            os.getenv("HOME"),
            ".config/autostart/calendar-indicator-autostart.desktop")
        self.options['autostart'].set_active(os.path.exists(filestart))

    def on_options_changed(self, widget, data):
        configuration = Configuration()
        configuration.set('time', self.options['time'].get_value())
        if self.options['theme'].get_active():
            configuration.set('theme','dark')
        else:
            configuration.set('theme','light')
        configuration.save()


    def on_options_autostart_changed(self, widget, data):
        filestart = os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")
        if not self.options['autostart'].get_active():
            if not os.path.exists(filestart):
                if not os.path.exists(os.path.dirname(filestart)):
                    os.makedirs(os.path.dirname(filestart))
                shutil.copyfile('/opt/extras.ubuntu.com/calendar-indicator/share/calendar-indicator/calendar-indicator-autostart.desktop',filestart)
        else:
            if os.path.exists(filestart):
                os.remove(filestart)

