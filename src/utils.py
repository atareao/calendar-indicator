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

import random

def tohex():
    val = '%x'%random.randint(0, 16777215)
    if len(val[1:])<6:
        val = '#'+(6-len(val[1:]))*'0'+val[1:]
    return val

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def contraste(hexvalue):
    r,g,b = hex_to_rgb(hexvalue)
    a =1 - ( 0.299 * r + 0.587 * g + 0.114 * b)/255.
    if a < 0.5:
        d = 0
    else:
        d = 255
    return  rgb_to_hex((d,d,d))