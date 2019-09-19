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
    gi.require_version('GObject', '2.0')
    gi.require_version('WebKit2', '4.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import WebKit2
from gi.repository import GObject
import comun

class LoginDialog(Gtk.Dialog):
    def __init__(self,url):
        self.code = None
        Gtk.Dialog.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_icon_from_file(comun.ICON)

        vbox = Gtk.VBox(spacing = 5)
        self.get_content_area().add(vbox)
        hbox1 = Gtk.HBox()
        vbox.pack_start(hbox1,True,True,0)

        self.scrolledwindow1 = Gtk.ScrolledWindow()
        self.scrolledwindow1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow1.set_shadow_type(Gtk.ShadowType.IN)
        hbox1.pack_start(self.scrolledwindow1,True,True,0)

        self.viewer = WebKit2.WebView()
        self.scrolledwindow1.add(self.viewer)
        self.scrolledwindow1.set_size_request(600,630)
        self.viewer.connect('load-changed', self.load_changed)
        self.viewer.load_uri(url)
        self.show_all()

    def load_changed(self, widget, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            print(widget)
            print(load_event)
            print(self.viewer.get_uri())
            try:
                uri = self.viewer.get_uri()
                print(uri)
                pos = uri.find('http://localhost/?code=')
                if pos > -1:
                    self.code = uri[23:]
                    self.hide()
            except Exception as e:
                print(e)
                print('Error')

if __name__ == '__main__':
    ld = LoginDialog('http://www.google.com')
    ld.run()
