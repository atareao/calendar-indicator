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

from gi.repository import Gtk, Gdk, GObject
from gi.repository import GdkPixbuf
import os
import shutil
import locale
import gettext
import datetime
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from logindialog import LoginDialog
from eventwindow import EventWindow
from preferences_dialog import get_calendar_from_options

import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

DAY_OF_WEEK = [_('Monday'),_('Tuesday'),_('Wednesday'),_('Thursday'),_('Friday'),_('Saturday'),_('Sunday')]

def first_day_of_month(adatetime):
	adatetime = adatetime.replace(day=1)
	return adatetime.weekday()

class DayWidget(Gtk.EventBox):
	__gsignals__ = {
		'edited' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
	}	
	def __init__(self,googlecalendar=None,adate=None, callback = None):		
		Gtk.EventBox.__init__(self)		
		self.set_size_request(150, 100)
		box1 = Gtk.Box.new(Gtk.Orientation.VERTICAL,0)
		self.add(box1)
		box2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,0)
		box1.pack_start(box2,True,True,padding=2)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.NONE)
		box2.pack_start(scrolledwindow,True,True,padding=2)
		self.store = Gtk.ListStore(str, object,str,str)
		self.treeview = Gtk.TreeView(self.store)
		self.treeview.connect('button-release-event',self.on_button_released_event)
		self.column = Gtk.TreeViewColumn('',  Gtk.CellRendererText(), text=0, background=2,foreground=3)
		self.treeview.append_column(self.column)
		scrolledwindow.add(self.treeview)
		if adate is not None:
			self.set_date(adate)
		self.googlecalendar = googlecalendar
		self.calendars = googlecalendar.calendars.values()
		self.callback = callback
		
	def on_button_released_event(self,widget,key):
		if self.calendars is not None:
			selection = widget.get_selection()
			if selection is not None:
				amodel,aiter = selection.get_selected()
				if amodel is not None and aiter is not None:
					aevent = amodel.get_value(aiter,1)
					ew = EventWindow(self.calendars,aevent)
					if ew.run() == Gtk.ResponseType.ACCEPT:
						if ew.get_operation() == 'DELETE':
							ew.destroy()
							md = Gtk.MessageDialog(	parent = None,
													flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
													type = Gtk.MessageType.ERROR,
													buttons = Gtk.ButtonsType.OK_CANCEL,
													message_format = _('Are you sure you want to revove this event?'))
							if md.run() == Gtk.ResponseType.OK:
								md.destroy()					
								if self.googlecalendar.remove_event(aevent['calendar_id'],aevent['id']):
									self.googlecalendar.calendars[aevent['calendar_id']]['events'].pop(aevent['id'],True)
									self.emit('edited')
									self.callback()
							md.destroy()
						elif ew.get_operation() == 'EDIT':
							event_id = aevent['id']
							calendar_id = ew.get_calendar_id()
							summary = ew.get_summary()
							start_date = ew.get_start_date()
							end_date = ew.get_end_date()
							description = ew.get_description()
							ew.destroy()
							md = Gtk.MessageDialog(	parent = None,
													flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
													type = Gtk.MessageType.ERROR,
													buttons = Gtk.ButtonsType.OK_CANCEL,
													message_format = _('Are you sure you want to edit this event?'))
							if md.run() == Gtk.ResponseType.OK:
								md.destroy()					
								edit_event = self.googlecalendar.edit_event(calendar_id, event_id, summary, start_date, end_date, description)
								if edit_event is not None:
									self.googlecalendar.calendars[calendar_id]['events'][edit_event['id']] = edit_event
									self.emit('edited')
									self.callback()
							md.destroy()
					ew.destroy()
				selection.unselect_all()
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
			calendar_options = get_calendar_from_options(configuration.get('calendars'),event['calendar_id'])
			if calendar_options:
				background_color = calendar_options['background']
				foreground_color = calendar_options['foreground']
				visible = calendar_options['visible']
			else:
				background_color = tohex(random.randint(0, 16777215))
				foreground_color = tohex(random.randint(0, 16777215))
				visible = True
			if event is not None:
				self.store.append([label,event,background_color,foreground_color])
	def set_background_color(self,color):
		self.treeview.modify_bg(Gtk.StateType.NORMAL, color)

	def set_foreground_color(self,color):
		self.treeview.modify_fg(Gtk.StateType.NORMAL, color)
	
		
class CalendarWindow(Gtk.Dialog):
	def __init__(self,googlecalendar = None, adate = None, calendars = []):
		self.googlecalendar = googlecalendar
		self.calendars = calendars
		#self.modify_bg(Gtk.StateType.NORMAL,Gdk.color_parse('#FFFFFF'))
		
		title = comun.APPNAME + ' | '+_('Calendar')
		Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.set_size_request(1200, 800)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		self.edited = False
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().pack_start(vbox0,True,True,0)
		#
		frame0 = Gtk.Frame()
		vbox0.pack_start(frame0,False,False,0)
		#
		hbox1 = Gtk.HBox()
		frame0.add(hbox1)
		#
		button0 = Gtk.Button()
		button0.set_size_request(40,40)
		button0.set_tooltip_text(_('One year less'))
		button0.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GOTO_FIRST,Gtk.IconSize.BUTTON))
		button0.connect('clicked',self.on_button0_clicked)
		hbox1.pack_start(button0,False,False,0)
		#
		button1 = Gtk.Button()
		button1.set_size_request(40,40)
		button1.set_tooltip_text(_('One month less'))
		button1.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_BACK,Gtk.IconSize.BUTTON))
		button1.connect('clicked',self.on_button1_clicked)
		hbox1.pack_start(button1,False,False,0)
		#
		self.monthyear = Gtk.Label('Month - Year')
		hbox1.pack_start(self.monthyear,True,True,0)
		#
		button2 = Gtk.Button()
		button2.set_size_request(40,40)
		button2.set_tooltip_text(_('One month more'))
		button2.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_FORWARD,Gtk.IconSize.BUTTON))
		button2.connect('clicked',self.on_button2_clicked)
		hbox1.pack_start(button2,False,False,0)
		#
		button3 = Gtk.Button()
		button3.set_size_request(40,40)		
		button3.set_tooltip_text(_('One year more'))
		button3.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GOTO_LAST,Gtk.IconSize.BUTTON))
		button3.connect('clicked',self.on_button3_clicked)
		hbox1.pack_start(button3,False,False,0)
		#
		
		#
		frame1 = Gtk.Frame()
		vbox0.pack_start(frame1,True,True,0)
		#
		hbox2 = Gtk.HBox()
		vbox0.pack_start(hbox2,False,False,0)
		#		
		button4 = Gtk.Button()
		button4.set_size_request(40,40)		
		button4.set_tooltip_text(_('Today'))			
		image = Gtk.Image()
		image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(comun.ICONDIR,'%s-light-normal.svg'%(datetime.datetime.now().day)),35,35))
		button4.set_image(image)
		button4.connect('clicked',self.on_button4_clicked)
		hbox2.pack_start(button4,False,False,0)
		#
		button5 = Gtk.Button()
		button5.set_size_request(40,40)		
		button5.set_tooltip_text(_('Close'))		
		button5.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_OK,Gtk.IconSize.BUTTON))
		button5.connect('clicked',self.on_button5_clicked)
		hbox2.pack_end(button5,False,False,0)
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		frame1.add(scrolledwindow)
		#
		table1 = Gtk.Table(rows = 7, columns = 8, homogeneous = False)
		table1.override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(1.,1.,1.,0))
		table1.set_border_width(2)
		table1.set_col_spacings(2)
		table1.set_row_spacings(2)
		scrolledwindow.add(table1)
		#
		self.days = {}
		self.week_days = {}
		contador = 0
		for row in range(1,7):
			self.week_days[row] = Gtk.Label(str(row))
			table1.attach(self.week_days[row],0,0+1,row,row+1,xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		for column in range(1,8):
			table1.attach(Gtk.Label(DAY_OF_WEEK[column-1]),column,column+1,0,1,xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		for row in range(1,7):
			for column in range(1,8):
				self.days[contador] = DayWidget(self.googlecalendar,callback=self.update)
				self.days[contador].connect('edited',self.on_edited)
				table1.attach(self.days[contador],column,column+1,row,row+1,xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.EXPAND)
				contador += 1
		#
		if adate is None:
			self.adate = datetime.datetime.now()
		else:
			self.adate = adate
		#
		self.set_date()
		#
		self.show_all()

	def on_edited(self,widget):
		self.edited = True

	def get_edited(self):
		return self.edited
		
	def close_application(self,widget):
		self.ok = False

	def set_date(self):
		self.monthyear.set_text(self.adate.strftime('%B - %Y'))
		fdom = first_day_of_month(self.adate)
		adate = self.adate.replace(day=1)
		for row in range(1,7):
			wd = adate + datetime.timedelta(days=7*(row-1))
			self.week_days[row].set_text(str(wd.isocalendar()[1]))
		for contador in range(0,42):
			if contador < fdom:
				tadate = adate - datetime.timedelta(days=(fdom-contador))
			else:
				tadate = adate + datetime.timedelta(days=(contador-fdom))
			self.days[contador].set_date(tadate)
			if tadate.month != adate.month:
				self.days[contador].set_background_color(Gdk.color_parse('#DDDDDD'))				
				self.days[contador].override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(1.,1.,1.,1))
			elif tadate.date() == datetime.datetime.today().date():
				self.days[contador].set_background_color(Gdk.color_parse('#FFFFFF'))
				self.days[contador].override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(1.0,0.0,0.0,1))
			else:
				self.days[contador].set_background_color(Gdk.color_parse('#FFFFFF'))
				self.days[contador].override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(1.,1.,1.,1))
		if self.googlecalendar is not None:
			events = self.googlecalendar.getAllEventsOnMonth(self.adate,calendars=self.calendars)
			for adate in events.keys():
				eventsday = events[adate]
				
			for contador in range(0,42):
				if self.days[contador].get_date().date() in events.keys():
					eventsday = events[self.days[contador].get_date().date()]
					if len(eventsday)>0:
						self.days[contador].set_events(eventsday)
					else:
						self.days[contador].clear()
				else:
					self.days[contador].clear()
			
	def update(self):
		if self.googlecalendar is not None:
			events = self.googlecalendar.getAllEventsOnMonth(self.adate)
			for contador in range(0,42):
				if self.days[contador].get_date().date() in events.keys():
					eventsday = events[self.days[contador].get_date().date()]
					if len(eventsday)>0:
						self.days[contador].set_events(eventsday)
					else:
						self.days[contador].clear()
				else:
					self.days[contador].clear()
		
	def on_button0_clicked(self,widget):
		year = self.adate.year - 1
		if year<1:
			year = 1
		self.adate = self.adate.replace(year=year)
		self.set_date()
		
	def on_button1_clicked(self,widget):
		month = self.adate.month-1
		if month < 1:
			month = 12
			year = self.adate.year-1
			if year < 1:
				year = 1
			self.adate = self.adate.replace(month=month,year=year)
		else:
			self.adate = self.adate.replace(month=month)
		self.set_date()
	
	def on_button2_clicked(self,widget):
		month = self.adate.month+1
		if month > 12:
			month = 1
			year = self.adate.year+1
			self.adate = self.adate.replace(month=month,year=year)
		else:
			self.adate = self.adate.replace(month=month)
		self.set_date()
	
	def on_button3_clicked(self,widget):
		self.adate = self.adate.replace(year=(self.adate.year+1))
		self.set_date()

	def on_button4_clicked(self,widget):
		today = datetime.datetime.today().date()
		self.adate = self.adate.replace(month=today.month,year=today.year)
		self.set_date()
	def on_button5_clicked(self,widget):
		self.hide()
		self.destroy()
		
		
		
if __name__ == "__main__":
	p = CalendarWindow()
	if p.run() == Gtk.ResponseType.ACCEPT:
		pass
	p.destroy()
	exit(0)
		
