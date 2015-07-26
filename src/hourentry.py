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

class HourEntry(Gtk.HBox):
	def __init__(self,value=None):
		Gtk.HBox.__init__(self)
		self.set_no_show_all(True)
		self.hour = Gtk.SpinButton()
		self.hour.set_width_chars(2)
		self.hour.set_adjustment(Gtk.Adjustment(value=0, lower=0, upper=23, step_incr=1, page_incr=5))
		self.hour.set_digits(0)		
		self.minute = Gtk.SpinButton()
		self.minute.set_width_chars(2)
		self.minute.set_adjustment(Gtk.Adjustment(value=0, lower=0, upper=59, step_incr=5, page_incr=10))
		self.minute.set_digits(0)
		self.pack_start(self.hour, 0, 0, 0)
		self.label = Gtk.Label(':')
		self.pack_start(self.label, 0, 0, 0)
		self.pack_start(self.minute, 0, 0, 0)

	def set_editable(self,editable):
		self.hour.set_editable(editable)
		self.minute.set_editable(editable)
	
	def set_sensitive(self,sensitive):
		self.hour.set_sensitive(sensitive)
		self.minute.set_sensitive(sensitive)

	def set_visible(self,visible):
		if visible:
			self.show()
			self.hour.show_all()
			self.minute.show_all()
			self.label.show_all()
		else:
			self.hide()			

	def get_time(self):
		h = self.hour.get_value_as_int()
		m = self.minute.get_value_as_int()
		return datetime.time(h,m)
	
	def set_time(self,time):
		self.hour.set_value(time.hour)
		self.minute.set_value(time.minute)

