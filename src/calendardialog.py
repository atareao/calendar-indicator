#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$06-jun-2010 12:34:44$'
#
# <one line to give the program's name and a brief idea of what it does.>
#
# Copyright (C) 2010 Lorenzo Carbonell
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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import locale
import gettext
#
import comun


locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


def get_date(event,start=True):
	if start:
		key = 'start'
	else:
		key = 'end'
	if 'dateTime' in event[key]:		
		return event[key]['dateTime']
	else:
		return event[key]['date']

def getDay(cadena):
	if cadena.find('T') == 0:
		return cadena.split('-')[2]
	else:
		return cadena.split('T')[0].split('-')[2]

def getMonth(cadena):
	print(cadena)
	if cadena.find('T') == 0:
		return int(cadena.split('-')[1])
	else:
		return int(cadena.split('T')[0].split('-')[1])
def getYear(cadena):
	print(cadena)
	if cadena.find('T') == 0:
		return int(cadena.split('-')[0])
	else:
		return int(cadena.split('T')[0].split('-')[0])


class CalendarDialog(Gtk.Dialog):
	def __init__(self,title,parent = None,googlecalendar = None,calendar_id = None):
		self.ok = False
		self.googlecalendar = googlecalendar
		self.calendar_id = calendar_id
		self.selecteds = {}
		#
		title = comun.APP + ' | '+_('Preferences')
		Gtk.Dialog.__init__(self,title,parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_default_size(50, 450)
		self.set_resizable(False)
		#self.set_icon_from_file(comun.ICON)		
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		self.calendar = Gtk.Calendar()
		self.calendar.set_property('show-day-names',True)
		self.calendar.set_property('show-heading',True)
		self.calendar.set_property('show-week-numbers',True)
		self.calendar.connect('month-changed',self.on_month_changed)
		self.calendar.connect('day-selected',self.on_day_selected)
		vbox0.add(self.calendar)
		self.on_month_changed(self)
		#
		self.show_all()
	def on_day_selected(self,widget):
		date = self.calendar.get_date()
		print('day -> %s' %(date[2]))
		print('month -> %s' %(date[1]+1))
		print('year -> %s' %(date[0]))
		if date[2] in self.selecteds.keys():
			self.calendar.set_tooltip_text(self.selecteds[date[2]])
		else:
			self.calendar.set_tooltip_text('')

	def on_month_changed(self,widget):
		date = self.calendar.get_date()
		self.selecteds = {}
		self._clear_marks()
		if self.googlecalendar != None:
			events = self.googlecalendar.getAllEventsOnMonthOnDefaultCalendar(self.calendar_id,date[1]+1,date[0])
			for event in events:
				month = getMonth(get_date(event))
				year = getYear(get_date(event))
				if month == date[1]+1 and date[0] == year:
					dia = getDay(get_date(event))
					self.selecteds[int(dia)] = event['summary']
			self._mark_days()
			
	def _unmark_days(self):
		for key in self.selecteds.keys():
			self.calendar.unmark_day(key)

	def _mark_days(self):
		for key in self.selecteds.keys():
			print(key)
			self.calendar.mark_day(key)
	def _clear_marks(self):
		self.calendar.clear_marks()
			
	def close_application(self,widget):
		self.ok = False
		self.hide()

if __name__ == "__main__":
	cd = CalendarDialog('')
	cd.run()
	exit(0)
		
