
import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('Handy', '0.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Handy
import os
import urllib
import comun
from comun import _
from sidewidget import SideWidget
from settingsrow import SettingRow
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from utils import tohex, hex_to_rgb, rgb_to_hex, contraste


def get_calendar_from_options(calendars_options,calendar_id):
    for calendar_options in calendars_options:
        if calendar_id == calendar_options['id']:
            return calendar_options
    return None


class CalendarOption(Gtk.Overlay):

    def __init__(self, googlecalendar=None):
        Gtk.Overlay.__init__(self)
        self.googlecalendar = googlecalendar
        self.__set_ui()

    def __set_ui(self):
        handycolumn = Handy.Column()
        handycolumn.set_maximum_width(700)
        handycolumn.set_margin_top(24)
        self.add(handycolumn)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        handycolumn.add(box)

        label = Gtk.Label(_('Calendars'))
        label.set_name('special')
        label.set_alignment(0, 0.5)
        box.add(label)

        listbox0 = Gtk.ListBox()
        box.add(listbox0)

        self.option = Gtk.Switch()
        self.option.set_valign(Gtk.Align.CENTER)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(700,300)

        self.store = Gtk.ListStore(str, str,str,str,bool,str)
        self.treeview = Gtk.TreeView(self.store)
        self.treeview.connect ('button-press-event', self.onclick)
        column1 = Gtk.TreeViewColumn(_('Calendar'), Gtk.CellRendererText(),
                                     text=0)
        self.treeview.append_column(column1)
        self.column2 = Gtk.TreeViewColumn(_('Background color'),
                                          Gtk.CellRendererText(), background=1)
        self.treeview.append_column(self.column2)
        self.column3 = Gtk.TreeViewColumn(_('Text color'),
                                          Gtk.CellRendererText(), background=2)
        self.treeview.append_column(self.column3)
        cellrenderer_toggle = Gtk.CellRendererToggle()
        cellrenderer_toggle.connect("toggled", self.cell_toggled, self.store)
        self.column4 = Gtk.TreeViewColumn(_('Show calendar'),
                                          cellrenderer_toggle, active=4)
        self.treeview.append_column(self.column4)
        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)
        renderer_editabletext.connect("edited", self.text_edited, self.store)
        self.column5 = Gtk.TreeViewColumn(_('Calendar name'), 
                                          renderer_editabletext, text=5,
                                          background=1, foreground=2)
        self.treeview.append_column(self.column5)
        scrolledwindow.add(self.treeview)

        listbox0.add(scrolledwindow)

    def onclick(self,widget,event):
        tp,tc,x,y = self.treeview.get_path_at_pos(event.x,event.y)
        if tc==self.column2:
            colordialog = Gtk.ColorSelectionDialog(_('Select background color'))
            colordialog.get_color_selection().set_current_color(
                Gdk.color_parse(self.store[tp][1]))
            if colordialog.run() == Gtk.ResponseType.OK:
                color = colordialog.get_color_selection().get_current_color().to_string()
                self.store[tp][1] = color
                self.on_change()
            colordialog.destroy()
        elif tc==self.column3:
            colordialog = Gtk.ColorSelectionDialog(_('Select foreground color'))
            colordialog.get_color_selection().set_current_color(
                Gdk.color_parse(self.store[tp][2]))
            if colordialog.run() == Gtk.ResponseType.OK:
                color = colordialog.get_color_selection().get_current_color().to_string()
                self.store[tp][2] = color
                self.on_change()
            colordialog.destroy()

    def cell_toggled(self, widget, path, model):
        all_invisible = True
        old_status = model[path][4]
        model[path][4] = not model[path][4]
        for row in model:
            if row[4] == True:
                all_invisible = False
                break
        if all_invisible:
            model[path][4] = True
        if old_status != model[path][4]:
            self.on_change()

    def text_edited(self, widget, path, text, model):
        model[path][5] = text
        self.on_change()

    def set_active(self):
        self.store.clear()
        configuration = Configuration()
        calendars_options = configuration.get('calendars')
        if os.path.exists(comun.TOKEN_FILE):
            if self.googlecalendar is not None:
                calendars = self.googlecalendar.calendars.values()
            else:
                gca = GoogleCalendar(token_file = comun.TOKEN_FILE)
                gca.read()
                calendars = gca.get_calendars().values()
            for calendar in calendars:
                calendar_options = get_calendar_from_options(
                    configuration.get('calendars'),calendar['id'])
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
                self.store.append([calendar['summary'], background_color,
                                   foreground_color, calendar['id'],
                                   visible, calendar_name])

    def on_change(self):
        if os.path.exists(comun.TOKEN_FILE):
            configuration = Configuration()
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