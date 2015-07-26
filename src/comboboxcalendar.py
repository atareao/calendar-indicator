#! /usr/bin/python3
# -*- coding: iso-8859-15 -*-
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

from gi.repository import Gtk
import datetime

def f00(number):
	number = str(number)
	if len(number)<2:
		return '00'[:len(number)]+number
	return number

class ComboBoxCalendar(Gtk.HBox):
	def __init__(self, window, format="dmy", separator='/', value = datetime.date.today()):
		Gtk.HBox.__init__(self)
		self.format = format
		self.separator = separator
		self._window = window
		self.entry = Gtk.Entry()
		self.entry.set_editable(False)
		self.button = Gtk.Button()
		self.button.add(Gtk.Arrow.new(Gtk.ArrowType.DOWN, Gtk.ShadowType.IN))
		self.button.connect('clicked', self.on_button)
		self.pack_start(self.entry, 0, 0, 0)
		self.pack_start(self.button, 0, 0, 0)
		self.month_changed = False
		self.set_date(value)

	def set_format(self, format):
		"""Sets the way, the date is formatted, value can be 'dmy' or 'ymd'."""
		self.format = format
		self.format_date()
		
	def get_format(self):
		return self.format
	
	def set_separator(self, separator):
		"""Sets the char used as separator for formatting date values"""
		self.__separator = separator
		self.format_date()
		
	def get_separator(self):
		return self.separator
		
	def set_sensitive(self, is_sensistive):
		self.entry.set_sensitive(is_sensistive)
		self.button.set_sensitive(is_sensistive)

	def set_editable(self, is_editable):
		self.entry.set_editable(is_editable)
		self.button.set_editable(is_editable)

	def on_button(self, button):
		win_position = self._window.get_position()
		x_win = win_position[0] + self.entry.get_allocation().x + 3
		y_win = win_position[1] + self.entry.get_allocation().y + 2*self.entry.get_allocation().height + 3
		self.dialog = Gtk.Dialog(None, None, Gtk.DialogFlags.MODAL)
		self.dialog.set_decorated(False)
		self.dialog.move(x_win, y_win)
		
		self.calendar = Gtk.Calendar()
		#
		self.calendar.select_month(self.date.month-1,self.date.year)
		self.calendar.select_day(self.date.day)
		#
		self.calendar.show()
		self.dialog.vbox.pack_start(self.calendar, 0, 0, 0)
		self.dialog.connect('focus-out-event',self.on_focus_out)
		self.calendar.connect('day-selected', self.on_select)
		self.calendar.connect('month-changed', self.on_month_select)
		#
		self.dialog.run()
		value = self.calendar.get_date()
		value = datetime.date(value[0],value[1]+1,value[2])
		self.set_date(value)
		self.dialog.destroy()

	def on_focus_out(self,widget,event):
		self.dialog.destroy()
		
	def set_date(self, value):
		self.date = value # datetime.date
		if type(value) is datetime.date:
			if self.format == "dmy":
				datestr = f00(value.day)+self.separator+f00(value.month)+self.separator+f00(value.year)
			elif self.format == "ymd":
				datestr = f00(value.year)+self.separator+f00(value.month)+self.separator+f00(value.day)
			self.entry.set_text(datestr)
		if type(value) is datetime.datetime:
			value = datetime.date(value.year,value.month,value.day)
			self.set_date(value)
		if type(value) is str:
			value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S.%fZ')
			value = datetime.date(value.year,value.month,value.day)
			self.set_date(value)
					
	def on_select(self,widget):
		if not self.month_changed:
			self.dialog.destroy()
		self.month_changed = False

	def get_date(self):
		return self.date
	
	def on_month_select(self,widget):
		self.month_changed = True
