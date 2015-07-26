#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$19/02/2012$'
#
#
# Copyright (C) 2011,2012 Lorenzo Carbonell
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

from gi.repository import Gtk, Gdk
import os
import shutil
import locale
import gettext
import datetime
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from logindialog import LoginDialog
import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

DAY_OF_WEEK = [_('Monday'),_('Tuesday'),_('Wednesday'),_('Thursday'),_('Friday'),_('Saturday'),_('Sunday')]

def first_day_of_month(adatetime):
	adatetime = adatetime.replace(day=1)
	return adatetime.weekday()

class DayWidget(Gtk.VBox):
	def __init__(self,adate=None):
		Gtk.VBox.__init__(self)
		self.set_size_request(150, 100)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		self.pack_start(scrolledwindow,True,True,0)
		self.store = Gtk.ListStore(str, object,str)
		self.treeview = Gtk.TreeView(self.store)
		self.column = Gtk.TreeViewColumn('',  Gtk.CellRendererText(), text=0, background=2)
		self.treeview.append_column(self.column)
		scrolledwindow.add(self.treeview)
		if adate is not None:
			self.set_date(adate)		

	def set_date(self,adate):
		self.adate = adate
		self.column.set_title(str(adate.day))

	def get_date(self):
		return self.adate
		
	def clear(self):
		self.store.clear()
		
	def set_events(self,events):
		configuration = Configuration()
		self.store.clear()
		for event in events:
			label = ''
			if 'summary' in event.keys():
				label = event['summary']
			if configuration.has(event['calendar_id']):
				color = configuration.get(event['calendar_id'])
			else:
				color = '#AFDEDF'
			self.store.append([label,event,color])
	def set_background_color(self,color):
		self.treeview.modify_bg(Gtk.StateType.NORMAL, color)
	
		
class AddCalendarWindow(Gtk.Dialog):
	def __init__(self):
		title = comun.APPNAME + ' | '+_('Calendar')
		Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT))
		self.set_size_request(300, 50)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		frame1 = Gtk.Frame()
		vbox0.add(frame1)
		#
		table1 = Gtk.Table(rows = 1, columns = 2, homogeneous = False)
		table1.set_border_width(2)
		table1.set_col_spacings(2)
		table1.set_row_spacings(2)
		frame1.add(table1)
		#
		label = Gtk.Label(_('Calendar name')+':')
		label.set_alignment(0.,0.5)
		table1.attach(label,0,1,0,1,xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.entry = Gtk.Entry()
		self.entry.set_width_chars(30)
		table1.attach(self.entry,1,2,0,1,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		self.show_all()

	def close_application(self,widget):
		self.ok = False
	
if __name__ == "__main__":
	p = AddCalendarWindow()
	if p.run() == Gtk.ResponseType.ACCEPT:
		pass
	p.destroy()
	exit(0)
		
