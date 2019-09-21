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
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
import os
import shutil
import random
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from logindialog import LoginDialog
import comun
from comun import _
from utils import tohex, hex_to_rgb, rgb_to_hex, contraste

def get_calendar_from_options(calendars_options,calendar_id):
    for calendar_options in calendars_options:
        if calendar_id == calendar_options['id']:
            return calendar_options
    return None

class Preferences(Gtk.Dialog):
    def __init__(self,googlecalendar = None):
        self.googlecalendar = googlecalendar
        title = comun.APPNAME + ' | '+_('Preferences')
        Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
        self.set_size_request(700, 300)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        #
        vbox0 = Gtk.VBox(spacing = 5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        #
        notebook = Gtk.Notebook()
        vbox0.add(notebook)
        #
        frame1 = Gtk.Frame()
        notebook.append_page(frame1,tab_label = Gtk.Label(_('Login')))
        #
        table1 = Gtk.Table(rows = 1, columns = 2, homogeneous = False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        #
        label11 = Gtk.Label(_('Allow access to Google Calendar')+':')
        label11.set_alignment(0,.5)
        table1.attach(label11,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.switch1 = Gtk.Switch()
        self.switch1.connect('button-press-event',self.on_switch1_changed)
        self.switch1.connect('activate',self.on_switch1_changed)
        table1.attach(self.switch1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        frame2 = Gtk.Frame()
        notebook.append_page(frame2,tab_label = Gtk.Label(_('Calendar options')))
        table2 = Gtk.Table(rows = 1, columns = 1, homogeneous = False)
        table2.set_border_width(5)
        table2.set_col_spacings(5)
        table2.set_row_spacings(5)
        frame2.add(table2)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(700,300)
        table2.attach(scrolledwindow,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)

        self.store = Gtk.ListStore(str, str,str,str,bool,str)
        self.treeview = Gtk.TreeView(self.store)
        self.treeview.connect ('button-press-event', self.onclick)
        column1 = Gtk.TreeViewColumn(_('Calendar'),  Gtk.CellRendererText(), text=0)
        self.treeview.append_column(column1)
        self.column2 = Gtk.TreeViewColumn(_('Background color'),  Gtk.CellRendererText(), background=1)
        self.treeview.append_column(self.column2)
        self.column3 = Gtk.TreeViewColumn(_('Text color'),  Gtk.CellRendererText(), background=2)
        self.treeview.append_column(self.column3)
        cellrenderer_toggle = Gtk.CellRendererToggle()
        cellrenderer_toggle.connect("toggled", self.cell_toggled, self.store)
        self.column4 = Gtk.TreeViewColumn(_('Show calendar'),  cellrenderer_toggle, active=4)
        self.treeview.append_column(self.column4)
        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)
        renderer_editabletext.connect("edited", self.text_edited, self.store)
        self.column5 = Gtk.TreeViewColumn(_('Calendar name'),  renderer_editabletext, text=5,background=1,foreground=2)
        self.treeview.append_column(self.column5)
        scrolledwindow.add(self.treeview)
        #
        frame3 = Gtk.Frame()
        notebook.append_page(frame3,tab_label = Gtk.Label(_('Options')))
        table3 = Gtk.Table(rows = 2, columns = 2, homogeneous = False)
        table3.set_border_width(5)
        table3.set_col_spacings(5)
        table3.set_row_spacings(5)
        frame3.add(table3)
        #
        label21 = Gtk.Label(_('Time between automatic syncronizations (hours)')+':')
        label21.set_alignment(0,.5)
        table3.attach(label21,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.spin3 = Gtk.SpinButton()
        self.spin3.set_range(2,24)
        self.spin3.set_increments(2,4)
        table3.attach(self.spin3,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label22 = Gtk.Label(_('Autostart')+':')
        label22.set_alignment(0,.5)
        table3.attach(label22,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.switch4 = Gtk.Switch()
        table3.attach(self.switch4,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label23 = Gtk.Label(_('Theme light')+':')
        label23.set_alignment(0,.5)
        table3.attach(label23,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.switch5 = Gtk.Switch()
        table3.attach(self.switch5,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.load_preferences()
        #
        self.show_all()

    def text_edited(self, widget, path, text, model):
        print('*******************************************************')
        print(text)
        print(model[path][0])
        print(model[path][1])
        print(model[path][2])
        print(model[path][3])
        print(model[path][4])
        print(model[path][5])
        model[path][5] = text
        print('*******************************************************')

    def cell_toggled(self, widget, path, model):
        all_invisible = True
        model[path][4] = not model[path][4]
        for row in model:
            if row[4] == True:
                all_invisible = False
                break
        if all_invisible:
            model[path][4] = True

    def onclick(self,widget,event):
        tp,tc,x,y = self.treeview.get_path_at_pos(event.x,event.y)
        if tc==self.column2:
            colordialog = Gtk.ColorSelectionDialog(_('Select background color'))
            colordialog.get_color_selection().set_current_color(Gdk.color_parse(self.store[tp][1]))
            if colordialog.run() == Gtk.ResponseType.OK:
                color = colordialog.get_color_selection().get_current_color().to_string()
                self.store[tp][1] = color
            colordialog.destroy()
        elif tc==self.column3:
            colordialog = Gtk.ColorSelectionDialog(_('Select foreground color'))
            colordialog.get_color_selection().set_current_color(Gdk.color_parse(self.store[tp][2]))
            if colordialog.run() == Gtk.ResponseType.OK:
                color = colordialog.get_color_selection().get_current_color().to_string()
                self.store[tp][2] = color
            colordialog.destroy()

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
            self.store.clear()
            for calendar in googlecalendar.get_calendars().values():
                background = tohex()
                foreground = contraste(background)
                self.store.append([calendar['summary'],background,foreground,calendar['id'],True,calendar['summary']])

    def load_preferences(self):
        self.switch1.set_active(os.path.exists(comun.TOKEN_FILE))
        configuration = Configuration()
        time = configuration.get('time')
        theme = configuration.get('theme')
        calendars_options = configuration.get('calendars')
        self.spin3.set_value(time)
        if os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")):
            self.switch4.set_active(True)
        if theme == 'light':
            self.switch5.set_active(True)
        else:
            self.switch5.set_active(False)
        if os.path.exists(comun.TOKEN_FILE):
            if self.googlecalendar is not None:
                calendars = self.googlecalendar.calendars.values()
            else:
                gca = GoogleCalendar(token_file = comun.TOKEN_FILE)
                gca.read()
                calendars = gca.get_calendars().values()
            self.store.clear()
            for calendar in calendars:
                calendar_options = get_calendar_from_options(configuration.get('calendars'),calendar['id'])
                if calendar_options:
                    background_color = calendar_options['background']
                    foreground_color = calendar_options['foreground']
                    visible = calendar_options['visible']
                    if 'name' in calendar_options.keys():
                        calendar_name = calendar_options['name']
                    else:
                        calendar_name = calendar['summary']
                else:
                    background_color = tohex()
                    foreground_color = contraste(background_color)
                    visible = True
                    calendar_name = calendar['summary']
                self.store.append([calendar['summary'],background_color,foreground_color,calendar['id'],visible,calendar_name])

    def save_preferences(self):
        if os.path.exists(comun.TOKEN_FILE):
            configuration = Configuration()
            configuration.set('version',comun.VERSION)
            configuration.set('time',self.spin3.get_value())
            if self.switch5.get_active():
                configuration.set('theme','light')
            else:
                configuration.set('theme','dark')
            calendars = []
            aiter = self.store.get_iter_first()
            while(aiter is not None):
                calendar = {}
                calendar['id'] = self.store.get_value(aiter,3)
                calendar['background'] = self.store.get_value(aiter,1)
                calendar['foreground'] = self.store.get_value(aiter,2)
                calendar['visible'] = self.store.get_value(aiter,4)
                calendar['name'] = self.store.get_value(aiter,5)
                calendars.append(calendar)
                aiter = self.store.iter_next(aiter)
            configuration.set('calendars',calendars)
            configuration.save()
            filestart = os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")
            if self.switch4.get_active():
                if not os.path.exists(filestart):
                    if not os.path.exists(os.path.dirname(filestart)):
                        os.makedirs(os.path.dirname(filestart))
                    shutil.copyfile('/opt/extras.ubuntu.com/calendar-indicator/share/calendar-indicator/calendar-indicator-autostart.desktop',filestart)
            else:
                if os.path.exists(filestart):
                    os.remove(filestart)

    def close_application(self,widget):
        self.ok = False


if __name__ == "__main__":
    p = Preferences()
    if p.run() == Gtk.ResponseType.ACCEPT:
        p.save_preferences()
    p.destroy()
    exit(0)

