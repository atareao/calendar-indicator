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
    gi.require_version('GLib', '2.0')
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('Notify', '0.7')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GdkPixbuf
from gi.repository import Notify
import os
import urllib
import time
import dbus
import datetime
import webbrowser
from calendardialog import CalendarDialog
from calendarwindow import CalendarWindow
from addcalendarwindow import AddCalendarWindow
from eventwindow import EventWindow
from googlecalendarapi import GoogleCalendar
import comun
from configurator import Configuration
from preferences_dialog import Preferences
from comun import _

def wait(time_lapse):
    time_start = time.time()
    time_end = (time_start + time_lapse)
    while time_end > time.time():
        while Gtk.events_pending():
            Gtk.main_iteration()

def short_msg(msg,length=50):
    if len(msg)>length:
        return msg[:length]
    return msg

def internet_on():
    try:
        response=urllib.request.urlopen('http://google.com',timeout=1)
        return True
    except Exception as e:
        print(e)
    return False

def check_events(event1,event2):
    return event1['id'] == event2['id']
    
def is_event_in_events(an_event,events):
    for event in events:
        if check_events(an_event,event):
            return True
    return False

def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None):
    if text != None:
        menu_item = Gtk.ImageMenuItem.new_with_label(text)
        if icon:
            image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
            menu_item.set_image(image)
            menu_item.set_always_show_image(True)
    else:
        if icon == None:
            menu_item = Gtk.SeparatorMenuItem()
        else:
            menu_item = Gtk.ImageMenuItem.new_from_stock(icon, None)
            menu_item.set_always_show_image(True)
    if conector_event != None and conector_action != None:				
        menu_item.connect(conector_event,conector_action)
    menu_item.show()
    menu.append(menu_item)
    return menu_item

class EventMenuItem(Gtk.MenuItem):
    def __init__(self,label):
        Gtk.MenuItem.__init__(self,label)
        self.event = None

    def get_event(self):
        return self.event

    def set_event(self,event):
        self.event = event
        if 'summary' in event.keys():
            self.set_label(event.get_start_date_string()+' - '+short_msg(event['summary']))
        else:
            self.set_label(event.get_start_date_string())

class CalendarIndicator():
    def __init__(self):
        if dbus.SessionBus().request_name("es.atareao.calendar-indicator") != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
            print("application already running")
            exit(0)
        self.indicator = appindicator.Indicator.new('Calendar-Indicator', 'Calendar-Indicator', appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.notification = Notify.Notification.new('','', None)
        self.googlecalendar = GoogleCalendar(token_file = comun.TOKEN_FILE)
        error = True
        while(error):
            if self.googlecalendar.do_refresh_authorization() is None:
                p = Preferences()
                if p.run() == Gtk.ResponseType.ACCEPT:
                    p.save_preferences()
                p.destroy()
                self.googlecalendar = GoogleCalendar(token_file = comun.TOKEN_FILE)
                if (not os.path.exists(comun.TOKEN_FILE)) or (self.googlecalendar.do_refresh_authorization() is None):
                    md = Gtk.MessageDialog(	parent = None,
                                            flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                            type = Gtk.MessageType.ERROR,
                                            buttons = Gtk.ButtonsType.OK_CANCEL,
                                            message_format = _('You have to authorize Calendar-Indicator to manage your Google Calendar.\n Do you want to authorize?'))
                    if md.run() == Gtk.ResponseType.CANCEL:
                        exit(3)
                    md.destroy()
                else:
                    self.googlecalendar = GoogleCalendar(token_file = comun.TOKEN_FILE)
                    if self.googlecalendar.do_refresh_authorization() is None:
                        error = False
            else:
                error = False
        self.load_preferences()
        #
        self.events = []
        self.create_menu()
        self.sync()
        self.update_menu()
        self.actualization_time = time.time()
        GLib.timeout_add_seconds(60, self.work)

    def sync(self):
        self.googlecalendar.read()
        
    def load_preferences(self):
        configuration = Configuration()
        self.time = configuration.get('time')
        self.theme = configuration.get('theme')
        self.calendars = configuration.get('calendars')
        self.visible_calendars = []
        for calendar in self.calendars:
            if calendar['visible']:
                self.visible_calendars.append(calendar['id'])
                
    def work(self):
        self.update_menu(check=True)
        if (time.time()-self.actualization_time) > self.time*3600:
            if internet_on():
                self.sync()
            self.actualization_time = time.time()
        return True

    def create_menu(self):
        self.menu = Gtk.Menu()
        self.menu_today = add2menu(self.menu, text = datetime.datetime.now().strftime('%A, %d %B %Y'))
        add2menu(self.menu)
        self.menu_events = []
        
        for i in range(10):
            menu_event = EventMenuItem('%s'%i)			
            menu_event.show()
            menu_event.set_visible(False)
            menu_event.connect('activate',self.on_menu_event_activate)
            self.menu.append(menu_event)
            self.menu_events.append(menu_event)
        add2menu(self.menu)
        self.menu_add_new_calendar = add2menu(self.menu, text = _('Add new calendar'), conector_event = 'activate',conector_action = self.on_menu_add_new_calendar)
        self.menu_add_new_event = add2menu(self.menu, text = _('Add new event'), conector_event = 'activate',conector_action = self.on_menu_add_new_event)
        add2menu(self.menu)
        self.menu_refresh = add2menu(self.menu, text = _('Sync with google calendar'), conector_event = 'activate',conector_action = self.on_menu_refresh)
        self.menu_show_calendar = add2menu(self.menu, text = _('Show Calendar'), conector_event = 'activate',conector_action = self.menu_show_calendar_response)
        self.menu_preferences = add2menu(self.menu, text = _('Preferences'), conector_event = 'activate',conector_action = self.menu_preferences_response)
        add2menu(self.menu)
        menu_help = add2menu(self.menu, text =_('Help'))
        menu_help.set_submenu(self.get_help_menu())
        add2menu(self.menu)
        add2menu(self.menu, text = _('Exit'), conector_event = 'activate',conector_action = self.menu_exit_response)
        self.menu.show()
        self.indicator.set_menu(self.menu)		

    def set_menu_sensitive(self,sensitive = False):
        self.menu_add_new_calendar.set_sensitive(sensitive)
        self.menu_add_new_event.set_sensitive(sensitive)
        self.menu_refresh.set_sensitive(sensitive)
        self.menu_show_calendar.set_sensitive(sensitive)
        self.menu_preferences.set_sensitive(sensitive)
        self.menu_about.set_sensitive(sensitive)
        
    def update_menu(self,check=False):
        #
        now = datetime.datetime.now()
        normal_icon = os.path.join(comun.ICONDIR,'%s-%s-normal.svg'%(now.day,self.theme))
        starred_icon = os.path.join(comun.ICONDIR,'%s-%s-starred.svg'%(now.day,self.theme))
        #
        self.indicator.set_icon(normal_icon)
        self.indicator.set_attention_icon(starred_icon)		
        #
        events2 = self.googlecalendar.getNextTenEvents(self.visible_calendars)
        self.menu_today.set_label(now.strftime('%A, %d %B %Y'))
        if check and len(self.events)>0:
            for event in events2:
                if not is_event_in_events(event,self.events):
                    msg = _('New event:')+'\n'
                    if 'summary' in event.keys():
                        msg += event.get_start_date_string() + ' - '+ event['summary']
                    else:
                        msg += event.get_start_date_string()
                    self.notification.update('Calendar Indicator',msg,comun.ICON_NEW_EVENT)
                    self.notification.show()
            for event in self.events:
                if not is_event_in_events(event,events2):
                    msg = _('Event finished:') + '\n'
                    if 'summary' in event.keys():
                        msg += event.get_start_date_string()+' - '+event['summary']
                    else:
                        msg += event.get_start_date_string()
                    self.notification.update('Calendar Indicator',msg,comun.ICON_FINISHED_EVENT)
                    self.notification.show()
        self.events = events2
        for i,event in enumerate(self.events):
            self.menu_events[i].set_event(event)
            self.menu_events[i].set_visible(True)
        for i in range(len(self.events),10):
            self.menu_events[i].set_visible(False)
        now = datetime.datetime.now()
        if len(self.events)>0:
            com = self.events[0].get_start_date()
            if now.year == com.year and now.month == com.month and now.day == com.day and now.hour == com.hour:
                self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
            else:
                self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        while Gtk.events_pending():
            Gtk.main_iteration()
        

    def get_help_menu(self):
        help_menu =Gtk.Menu()
        #		
        add2menu(help_menu,text = _('In Launchpad'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://launchpad.net/calendar-indicator'))
        add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://answers.launchpad.net/calendar-indicator'))
        add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://translations.launchpad.net/calendar-indicator'))
        add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://bugs.launchpad.net/calendar-indicator'))
        add2menu(help_menu)
        web = add2menu(help_menu,text = _('Homepage'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.atareao.es/tag/calendar-indicator'))
        twitter = add2menu(help_menu,text = _('Follow us in Twitter'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://twitter.com/atareao'))
        googleplus = add2menu(help_menu,text = _('Follow us in Google+'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://plus.google.com/118214486317320563625/posts'))
        facebook = add2menu(help_menu,text = _('Follow us in Facebook'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.facebook.com/elatareao'))
        add2menu(help_menu)
        self.menu_about = add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.menu_about_response)
        #		
        web.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'web.svg')))
        web.set_always_show_image(True)
        twitter.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'twitter.svg')))
        twitter.set_always_show_image(True)
        googleplus.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'googleplus.svg')))
        googleplus.set_always_show_image(True)
        facebook.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'facebook.svg')))
        facebook.set_always_show_image(True)
        #
        help_menu.show()
        return help_menu

    def on_menu_add_new_event(self,widget):
        ew = EventWindow(self.googlecalendar.calendars.values())
        if ew.run() == Gtk.ResponseType.ACCEPT:
            calendar_id = ew.get_calendar_id()
            summary = ew.get_summary()
            start_date = ew.get_start_date()
            end_date = ew.get_end_date()
            description = ew.get_description()
            ew.destroy()
            new_event = self.googlecalendar.add_event(calendar_id, summary, start_date, end_date, description)
            if new_event is not None:
                self.googlecalendar.calendars[calendar_id]['events'][new_event['id']] = new_event
                self.update_menu(check=True)
        ew.destroy()

    def on_menu_event_activate(self,widget):
        ew = EventWindow(self.googlecalendar.calendars.values(),widget.get_event())
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
                    event = widget.get_event()
                    if self.googlecalendar.remove_event(event['calendar_id'],event['id']):
                        self.googlecalendar.calendars[event['calendar_id']]['events'].pop(event['id'],True)
                        self.update_menu(check=True)
                md.destroy()
            elif ew.get_operation() == 'EDIT':
                event = widget.get_event()
                event_id = event['id']
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
                        self.update_menu(check=True)
                md.destroy()
        ew.destroy()
        
    def on_menu_add_new_calendar(self,widget):
        acw = AddCalendarWindow()
        if acw.run() == Gtk.ResponseType.ACCEPT:
            calendar_name = acw.entry.get_text()
            acw.destroy()
            new_calendar = self.googlecalendar.add_calendar(calendar_name)
            if new_calendar is not None:
                self.googlecalendar.calendars[new_calendar['id']] = new_calendar
        acw.destroy()		
        
    def menu_preferences_response(self,widget):
        self.set_menu_sensitive(False)
        p1 = Preferences(self.googlecalendar)
        if p1.run() == Gtk.ResponseType.ACCEPT:
            p1.save_preferences()			
            if not os.path.exists(comun.TOKEN_FILE) or self.googlecalendar.do_refresh_authorization() is None:
                exit(-1)
            self.load_preferences()
            self.events = []	
            self.update_menu()		
        p1.destroy()
        self.set_menu_sensitive(True)
                    
    def menu_show_calendar_response(self,widget):
        self.set_menu_sensitive(False)
        cd = CalendarWindow(self.googlecalendar,calendars=self.visible_calendars)
        cd.run()
        edited =cd.get_edited()
        cd.destroy()
        if edited:
            self.update_menu(check=True)
        self.set_menu_sensitive(True)

    def on_menu_refresh(self,widget):
        self.sync()
        self.update_menu(check=True)
    
    def menu_exit_response(self,widget):
        exit(0)

    def menu_about_response(self,widget):
        self.set_menu_sensitive(False)
        ad=Gtk.AboutDialog()
        ad.set_name(comun.APPNAME)
        ad.set_version(comun.VERSION)
        ad.set_copyright('Copyrignt (c) 2011-2014\nLorenzo Carbonell')
        ad.set_comments(_('An indicator for Google Calendar'))
        ad.set_license(''+
        'This program is free software: you can redistribute it and/or modify it\n'+
        'under the terms of the GNU General Public License as published by the\n'+
        'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
        'any later version.\n\n'+
        'This program is distributed in the hope that it will be useful, but\n'+
        'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
        'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
        'more details.\n\n'+
        'You should have received a copy of the GNU General Public License along with\n'+
        'this program.  If not, see <http://www.gnu.org/licenses/>.')
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_translator_credits('Štefan Lučivjanský <https://launchpad.net/~stefan-lucivjansky>\n\
abuyop <https://launchpad.net/~abuyop>\n\
pisartshik <https://launchpad.net/~pisartshik>\n\
ma$terok <https://launchpad.net/~m-shein>\n\
Henrique Gressler <https://launchpad.net/~gresslerbwg>\n\
Luka Korošec <https://launchpad.net/~pizmovc>\n\
CJPark <https://launchpad.net/~pcjpcj2>\n\
Łukasz M <https://launchpad.net/~december0123>\n\
Miguel Anxo Bouzada <https://launchpad.net/~mbouzada>\n\
mgomezbuceta <https://launchpad.net/~mgomezbuceta>\n\
Wang Dianjin <https://launchpad.net/~tuhaihe>\n\
Bence Lukács <https://launchpad.net/~lukacs-bence1>\n\
Aliyar Güneş <https://launchpad.net/~aliyargunes>\n\
Antonio Vicién Faure <https://launchpad.net/~antoniopolonio>\n\
Manos Nikiforakis <https://launchpad.net/~nikiforakis-m>\n\
gogo <https://launchpad.net/~trebelnik-stefina>\n\
A.J. Baudrez <https://launchpad.net/~a.baudrez>\n\
simonbor <https://launchpad.net/~simon-bor>\n\
Jiri Grönroos <https://launchpad.net/~jiri-gronroos>\n')		
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_program_name(comun.APPNAME)
        ad.run()
        ad.destroy()
        self.set_menu_sensitive(True)

def main():
    Notify.init("calendar-indicator")
    CalendarIndicator()
    Gtk.main()

if __name__ == "__main__":
    main()