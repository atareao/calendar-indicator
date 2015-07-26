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
import locale
import gettext
import datetime
import comun
from comboboxcalendar import ComboBoxCalendar
from hourentry import HourEntry

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

class AddEventWindow(Gtk.Dialog):
	def __init__(self, calendars=None):
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
		table1 = Gtk.Table(rows = 7, columns = 3, homogeneous = False)
		table1.set_border_width(2)
		table1.set_col_spacings(2)
		table1.set_row_spacings(2)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('To calendar')+':')
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.liststore = Gtk.ListStore(str,str)		
		if calendars is not None:
			for calendar in calendars:
				self.liststore.append(calendar['summary'],calendar['id'])
		self.entry1 = Gtk.ComboBox.new_with_model(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		self.entry1.pack_start(renderer_text, True)
		self.entry1.add_attribute(renderer_text, "text", 0)
		self.entry1.set_active(0)
		table1.attach(self.entry1,1,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)						
		#
		label2 = Gtk.Label(_('Title')+':')
		label2.set_alignment(0.,0.5)
		table1.attach(label2,0,1,1,2,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.entry2 = Gtk.Entry()
		self.entry2.set_width_chars(30)
		table1.attach(self.entry2,1,3,1,2,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		label3 = Gtk.Label(_('All day event')+':')
		label3.set_alignment(0.,0.5)
		table1.attach(label3,0,2,2,3,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.entry3 = Gtk.CheckButton()
		self.entry3.connect('toggled',self.on_check_button_toggled)
		table1.attach(self.entry3,2,3,2,3,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)		
		#
		label4 = Gtk.Label(_('Start date')+':')
		label4.set_alignment(0.,0.5)
		table1.attach(label4,0,1,3,4,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.entry4 = HourEntry()
		self.entry4.set_visible(True)
		table1.attach(self.entry4,1,2,3,4,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)

		self.entry5 = ComboBoxCalendar(self)
		table1.attach(self.entry5,2,3,3,4,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		label5 = Gtk.Label(_('End date')+':')
		label5.set_alignment(0.,0.5)
		table1.attach(label5,0,1,4,5,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.entry6 = HourEntry()
		self.entry6.set_visible(True)
		table1.attach(self.entry6,1,2,4,5,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)

		self.entry7 = ComboBoxCalendar(self)
		table1.attach(self.entry7,2,3,4,5,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		label6 = Gtk.Label(_('Description')+':')
		label6.set_alignment(0.,0.5)
		table1.attach(label6,0,1,5,6,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
		scrolledwindow.set_size_request(300, 300)
		table1.attach(scrolledwindow,0,3,6,7,xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		self.entry8 = Gtk.TextView()
		self.entry8.set_wrap_mode(Gtk.WrapMode.WORD)
		scrolledwindow.add(self.entry8)		
		#
		self.show_all()
	
	def on_check_button_toggled(self,widget):
		is_on = not self.entry3.get_active()
		self.entry4.set_visible(is_on)
		self.entry6.set_visible(is_on)			
	
	def close_application(self,widget):
		self.hide()
	
	def get_calendar_id(self):
		tree_iter = self.entry1.get_active_iter()
		if tree_iter != None:
			model = self.entry1.get_model()
			return model[tree_iter][1]
		return None

	def get_summary(self):
		return self.entry2.get_text()

	def get_all_day_event(self):
		return self.entry3.get_active()
	
	def get_start_date(self):
		if self.entry3.get_active():
			return self.entry5.get_date()
		else:
			adate = self.entry5.get_date()
			atime = self.entry4.get_time()
			return datetime.datetime(adate.year,adate.month,adate.day,atime.hour,atime.minute)

	def get_end_date(self):
		if self.entry3.get_active():
			return self.entry7.get_date()
		else:
			adate = self.entry7.get_date()
			atime = self.entry6.get_time()
			return datetime.datetime(adate.year,adate.month,adate.day,atime.hour,atime.minute)
			
	def get_description(self):
		tbuffer =self.entry8.get_buffer()
		inicio = tbuffer.get_start_iter()
		fin = tbuffer.get_end_iter()
		description = tbuffer.get_text(inicio,fin,True)
		if len(description)>0:
			return description
		return None

				

if __name__ == "__main__":
	p = AddEventWindow()
	if p.run() == Gtk.ResponseType.ACCEPT:
		pass
	p.destroy()
	exit(0)
		
