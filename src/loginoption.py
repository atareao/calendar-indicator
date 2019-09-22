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
from comun import _
from sidewidget import SideWidget
from settingsrow import SettingRow
from logindialog import LoginDialog
from googlecalendarapi import GoogleCalendar


class LoginOption(Gtk.Overlay):

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

        label = Gtk.Label(_('Google calendar permissions'))
        label.set_name('special')
        label.set_alignment(0, 0.5)
        box.add(label)

        listbox0 = Gtk.ListBox()
        box.add(listbox0)

        self.switch1 = Gtk.Switch()
        self.switch1.connect('button-press-event',self.on_switch1_changed)
        self.switch1.connect('activate',self.on_switch1_changed)

        self.switch1.set_valign(Gtk.Align.CENTER)

        listbox0.add(SettingRow(_('Permissions for Google Calendar'),
                        _('Enable read and write permissions for Google Calendar.'),
                        self.switch1))

        self.switch1.set_active(os.path.exists(comun.TOKEN_FILE))

    def on_switch1_changed(self,widget,data):
        if self.switch1.get_active():
            if os.path.exists(comun.TOKEN_FILE):
                os.remove(comun.TOKEN_FILE)
        else:
            googlecalendar = GoogleCalendar(token_file = comun.TOKEN_FILE)
            if googlecalendar.do_refresh_authorization() is None:
                authorize_url = googlecalendar.get_authorize_url()
                ld = LoginDialog(authorize_url)
                ld.run()
                googlecalendar.get_authorization(ld.code)
                ld.destroy()
                if googlecalendar.do_refresh_authorization() is None:
                    md = Gtk.MessageDialog(	parent = self,
                                            flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                            type = Gtk.MessageType.ERROR,
                                            buttons = Gtk.ButtonsType.OK_CANCEL,
                                            message_format = _('You have to authorize Calendar-Indicator to use it, do you want to authorize?'))
                    if md.run() == Gtk.ResponseType.CANCEL:
                        exit(3)
                else:
                    if googlecalendar.do_refresh_authorization() is None:
                        exit(3)
                self.switch1.set_active(True)
