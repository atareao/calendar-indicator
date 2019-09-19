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

import sys
 
_login_success = False
def login():
  from gobject import MainLoop
  from dbus.mainloop.glib import DBusGMainLoop
  from ubuntuone.platform.credentials import CredentialsManagementTool
 
  global _login_success
  _login_success = False
 
  DBusGMainLoop(set_as_default=True)
  loop = MainLoop()
 
  def quit(result):
    global _login_success
    loop.quit()
    if result:
            _login_success = True
 
  cd = CredentialsManagementTool()
  d = cd.login()
  d.addCallbacks(quit)
  loop.run()
  if not _login_success:
    sys.exit(1)
 
if len(sys.argv) <= 1:
  login()
  sys.exit(1)
 
if sys.argv[1] == "login":
  login()
