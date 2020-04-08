#!/usr/bin/env python3

from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, Pango
import warnings, os, sys
from providers.filesystem import Filesystem
from providers.videos import Videos
import configparser
from enum import EnumMeta, Enum

class Config:
    cdir = os.path.join (os.path.expanduser ('~'), '.config/domino')
    if not os.path.exists (cdir):
        os.mkdir (cdir)
    cfile = os.path.join (cdir, 'config')
    config = configparser.ConfigParser ()
    config.read (cfile)
    
    def set (self, key, value, section = 'default'):
        if not section in self.config:
            self.config [section] = {}
        
        section = self.config [section]
        section [key] = value
        
        with open (self.cfile, 'w') as cfile:
            self.config.write (cfile)
    
    def get (self, key, section = 'default'):
        if section in self.config:
            if key in self.config [section]:
                return self.config [section][key]
        return None

class GenericWindow (Gtk.Window):
    icon_theme = Gtk.IconTheme.get_default ()

    def update (self):
        while self.mainloop.context.pending ():
            self.mainloop.context.iteration ()

    def __init__ (self):
        Gtk.Window.__init__ (self)
        self.connect ("destroy", lambda *w: self.main_quit ())
        self.connect ("key-press-event", self.hotkeys)
        self.mainloop = GLib.MainLoop ()
        self.mainloop.context = self.mainloop.get_context ()
        
    shortcuts = {
        Gdk.KEY_Escape: lambda self: self.main_quit (exit = True)
        #Gdk.KEY_Return: lambda self: self.main_quit ()
    }
    
    meta_shortcuts = {
        Gdk.KEY_q: lambda self: self.main_quit (exit = True),
        Gdk.KEY_w: lambda self: self.main_quit ()
    }

    def hotkeys (self, window, event):
        #print (int (event.state))
        if int (event.state) == 20 or int (event.state) == 4 or int (event.state) == 8 or int (event.state) == 24:
            if event.keyval in self.meta_shortcuts:
                self.meta_shortcuts [event.keyval] (self)
                return True

        elif event.keyval in self.shortcuts:
            self.shortcuts [event.keyval] (self)
            return True

    def update (self):
        while self.mainloop.context.pending ():
            self.mainloop.context.iteration ()

    def main (self):
        self.show_all ()
        try:
            self.mainloop.run ()
        except KeyboardInterrupt as e:
            print (e)
            self.main_quit ()

    def main_quit (self, exit = False):
        self.mainloop.quit ()
        sys.exit () if exit else None

class Tab (Gtk.Overlay):
    current_path = None
    
    def do_search_select (self):
        text = self.search.e.get_text ()
        if not len (text):
            return
        i = self.store.get_iter_first ()

        while i is not None:
            f = self.store.get (i, 1) [0]
            if text in f.lower () [:len (text)]:
                self.iconview.select_path (self.store.get_path (i))
                self.iconview.scroll_to_path (self.store.get_path (i), False, 0, 0)
                return
            i = self.store.iter_next (i)
    
    def do_search (self, begin = None):
        #self.search.r.set_reveal_child (True)
        #if begin is not None:
            #self.search.e.set_text (begin)
        self.search.set_search_mode (True)
    
    def reload (self):
        self.open (self.current_path)
    
    def popup_menu (self):
        sort = self.provider.get_sort_types ()
        menu = Gtk.Menu ()
        sort_menu = Gtk.Menu ()
        
        s_item = Gtk.MenuItem.new_with_mnemonic ('_Sort')
        reverse = Gtk.CheckMenuItem.new_with_mnemonic ('_Reverse')
        reverse.set_active (self.provider.get_sort_reverse ())
        reverse.connect ('activate', lambda *w: self.provider.set_sort_reverse (w [0].get_active ()))
        reverse.connect ('activate', lambda *w: self.reload ())
        sort_menu.append (reverse)
        sort_menu.append (Gtk.SeparatorMenuItem ())
        g = None
        for s in sort:
            item = Gtk.RadioMenuItem.new_with_mnemonic (g, s.replace (s [0], '_' + s [0], 1).title ())
            if g is None:
                g = [item]
            else:
                g.append (item)
            sort_menu.append (item)
            if self.provider.get_sort () == s:
                item.set_active (True)
            
            item.connect ('activate', lambda *w: self.provider.set_sort (w [0].get_label ()))
            item.connect ('activate', lambda *w: self.reload ())
            item.show ()
        
        s_item.set_submenu (sort_menu)
        menu.append (s_item)
        
        refresh = Gtk.MenuItem.new_with_mnemonic ('_Refresh')
        menu.append (Gtk.SeparatorMenuItem ())
        menu.append (refresh)
        refresh.connect ('activate', lambda *w: self.reload ())
        
        zoom_in = Gtk.MenuItem.new_with_mnemonic ('Zoom _in')
        zoom_out = Gtk.MenuItem.new_with_mnemonic ('Zoom _out')
        zoom_100 = Gtk.MenuItem.new_with_mnemonic ('Zoom _100')
        menu.append (Gtk.SeparatorMenuItem ())
        zoom_in.connect ('activate', lambda *w: self.ui.icon_zoom_in ())
        zoom_100.connect ('activate', lambda *w: self.ui.icon_reset ())
        zoom_100.connect ('activate', lambda *w: self.reload ())
        zoom_out.connect ('activate', lambda *w: self.ui.icon_zoom_out ())
        zoom_in.connect ('activate', lambda *w: self.reload ())
        zoom_out.connect ('activate', lambda *w: self.reload ())
        zoom_in.set_use_underline (True)
        zoom_out.set_use_underline (True)
        refresh.set_use_underline (True)
        menu.append (zoom_in)
        menu.append (zoom_out)
        menu.append (zoom_100)
        menu.show_all ()
        m = GLib.MainLoop ()
        menu.connect ('deactivate', lambda *w: m.quit ())
        menu.popup_for_device (None, None, None, None, None, 0, Gtk.get_current_event_time ())
        m.run ()
    
    def up (self):
         self.open (os.path.dirname (self.current_path))

    def config_load (self):
        if not hasattr (self.provider, 'config'):
            return
            
        for key in self.provider.config:
            value = self.ui.config.get (key, 'tab')
            if value is not None:
                if value.isdigit ():
                    setattr (self.provider, key, int (value))
                elif value == 'True':
                    setattr (self.provider, key, True)
                elif value == 'False':
                    setattr (self.provider, key, False)
                else:
                    setattr (self.provider, key, value)
            
    def config_save (self):
        if not hasattr (self.provider, 'config'):
            return
            
        for key in self.provider.config:
            value = getattr (self.provider, key)
            #print (isinstance (value, Enum))
            if isinstance (value, Enum):
                value = value.name
                if '.' in value:
                    value = value.split ('.') [-1]
                #print (value)
            elif not isinstance (value, str):
                value = str (value)
        #print (key, value, 'tab')
            self.ui.config.set (key, value, 'tab')
            
    def __init__ (self, ui, provider):
        #Gtk.ScrolledWindow.__init__ (self)
        super ().__init__ ()
        self.ui = ui
        self.build_ui ()
        self.provider = provider
        self.history = []
        self.config_load ()
        if provider:
            self.open (self.provider.default_path)
        self.connect ('destroy', lambda *w: self.provider.on_delete () if hasattr (self.provider, 'on_delete') else True)
        self.connect ('destroy', lambda *w: self.config_save ())
    
    def item_activated (self, iconview, path):
        it = self.store.get_iter (path)
        node = self.store.get (it, 2) [0]
        if self.provider.is_path (node):
            self.open (node)
        else:
            self.provider.open (node)

    def home (self):
        if self.provider:
            self.open (self.provider.default_path)
    
    def back (self):
        if self.current_path in self.history:
            current = self.history.index (self.current_path)
            if current > 0:
                self.open (self.history [current - 1])
        else:
            self.history.append (self.current_path)
            if len (self.history) > 1:
                self.open (self.history [-2])
            else:
                self.open (self.history [-1])

    def forward (self):
        if self.current_path in self.history:
            current = self.history.index (self.current_path)
            if current < len (self.history) - 1:
                self.open (self.history [current + 1])
        else:
            self.history.append (self.current_path)

    def open (self, path):
        self.current_path = path
        self.store.clear ()
        names = self.provider.get (path)
        for a in names:
            #print (a)
            self.store.append (a)
        self.ui.addressbar.set_text (path)
        self.ui.notebook.set_tab_label (self, Gtk.Label (os.path.basename (path)))
        #if path in self.history:
            #print (self.history, path)
            #self.history = self.history [:self.history.index (path)]
        #else:
        if not path in self.history:
            self.history.append (path)

    def build_ui (self):
        self.iconview = Gtk.IconView ()
        self.iconview.sw = Gtk.ScrolledWindow ()
        self.iconview.sw.add (self.iconview)
        self.iconview.connect ('item-activated', self.item_activated)
        self.iconview.set_activate_on_single_click (True)
        #self.pack_start (self.iconview.sw, 1, 1, 0)
        self.add (self.iconview.sw)
        self.store = Gtk.ListStore (GdkPixbuf.Pixbuf, str, str)
        self.store.set_sort_column_id (Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, 0)
        self.iconview.set_model (self.store)
        self.iconview.set_column_spacing (10)
        #self.iconview.set_columns (7)
        self.iconview.set_row_spacing (10)
        self.iconview.set_item_width (100)
        
        self.iconview.set_pixbuf_column (0)
        self.iconview.set_text_column (1)
        self.iconview.set_tooltip_column (2)
        
        self.search = Gtk.SearchBar ()
        self.search.e = Gtk.Entry ()
        self.search.e.connect ('activate', lambda *w: self.search.set_search_mode (False))
        self.search.e.connect ('activate', lambda *w: self.iconview.item_activated (self.iconview.get_selected_items () [0]))
        self.search.e.connect ('changed', lambda *w: self.do_search_select ())
        #self.search.connect ('hide', lambda *w: self.iconview.grab_focus ())
        self.search.add (self.search.e)
        #self.search.r = Gtk.Revealer ()
        #self.search.r.add (self.search)
        #self.pack_start (self.search, 0, 0, 0)
        self.search.props.valign = 2
        self.search.props.halign = 2
        self.add_overlay (self.search)
        self.show_all ()
        
class Window (GenericWindow):
    service_providers = dict () #{'dummy': None}
    ICON_SIZE = 96
    config = Config ()

    def icon_zoom_in (self, *w):
        self.ICON_SIZE += 24
        #print (self.ICON_SIZE)

    def icon_zoom_out (self, *w):
        self.ICON_SIZE -= 24

    def icon_reset (self, *w):
        self.ICON_SIZE = 96

    def __init__ (self):
        super (). __init__ ()
        self.build_ui ()
        self.init_autoconfig ()
        self.init_providers ()
        self.maximize ()
        self.provider.set_active (1)
        self.new_tab (self.provider.get_active_text ())

    def init_autoconfig (self):
        for i in self.service_providers:
            self.provider.append_text (i)
        
        self.set_size_request (640, 400)
    
    def init_providers (self):
        self.add_service_provider ('filesystem', Filesystem (self))
        self.add_service_provider ('videos', Videos (self))
    
    def add_shortcut (self, key, callback, meta = False):
        if meta:
            self.meta_shortcuts [key] = callback
        else:
            self.shortcuts [key] = callback
        
    def build_ui (self):
        self.hbox = Gtk.HBox ()
        self.vbox = Gtk.VBox ()
        self.hbox.pack_start (self.vbox, 1, 1, 0)
        self.grid = Gtk.Grid ()
        self.add (self.hbox)
        self.grid.set_column_spacing (10)
        self.grid.set_row_spacing (10)
        
        self.toolbar = Gtk.Toolbar ()
        self.toolbar.revealer = Gtk.Revealer ()
        self.toolbar.revealer.add (self.toolbar)
        self.toolbar.revealer.set_reveal_child (True)
        #self.grid.attach (self.toolbar, 0, 0, 1, 8)
        self.vbox.pack_start (self.toolbar.revealer, 0, 0, 0)
        
        self.add_shortcut (Gdk.KEY_F1, lambda *w: self.toolbar.revealer.set_reveal_child (not self.toolbar.revealer.get_reveal_child ()))
        
        self.toolbar.back = Gtk.ToolButton.new_from_stock ('gtk-go-back')
        self.toolbar.up = Gtk.ToolButton.new_from_stock ('gtk-go-up')
        self.toolbar.forward = Gtk.ToolButton.new_from_stock ('gtk-go-forward')
        self.toolbar.home = Gtk.ToolButton.new_from_stock ('gtk-home')

        self.toolbar.insert (self.toolbar.back, -1)
        self.toolbar.insert (self.toolbar.up, -1)
        self.toolbar.insert (self.toolbar.home, -1)
        self.toolbar.insert (self.toolbar.forward, -1)

        self.addressbar = Gtk.Entry ()
        self.addressbar.ti = Gtk.ToolItem ()
        self.addressbar.ti.add (self.addressbar)
        self.addressbar.ti.set_expand (True)
        
        self.provider = Gtk.ComboBoxText ()
        self.provider.ti = Gtk.ToolItem ()
        self.provider.ti.add (self.provider)

        self.notebook = Gtk.Notebook ()
        self.vbox.pack_start (self.notebook, 1, 1, 0)
        self.hbox.pack_start (self.grid, 0, 0, 0)
        #self.grid.attach (self.notebook, 0, 0, 1, 1)
        self.notebook.close = Gtk.Button ()
        self.notebook.close.set_relief (2)
        self.notebook.close.add (Gtk.Image.new_from_pixbuf (self.icon_theme.load_icon ('gtk-close', 24, Gtk.IconLookupFlags.GENERIC_FALLBACK)))
        self.notebook.close.show_all ()
        self.notebook.add = Gtk.ToolButton.new_from_stock ('gtk-add')
        #self.notebook.buttonbox = Gtk.ButtonBox ()
        #self.notebook.buttonbox.pack_start (self.notebook.add, 0, 0, 0)
        #self.notebook.buttonbox.pack_start (self.notebook.close, 0, 0, 0)
        self.notebook.set_action_widget (self.notebook.close, 1)
        self.toolbar.insert (self.provider.ti, -1)
        self.toolbar.insert (self.notebook.add, -1)
        self.toolbar.insert (self.addressbar.ti, -1)

        self.notebook.close.connect ('clicked', lambda *w: self.close_current_tab ())
        self.notebook.add.connect ('clicked', lambda *w: self.new_tab (self.provider.get_active_text ()))
        self.add_shortcut (Gdk.KEY_w, self.close_current_tab, meta = True)
        self.add_shortcut (Gdk.KEY_t, lambda *w: self.new_tab (self.provider.get_active_text ()), meta = True)
        
        self.addressbar.connect ('activate', lambda *w: self.open (self.addressbar.get_text ()))
        self.addressbar.connect ('activate', lambda *w: self.get_tab ().iconview.grab_focus ())
        self.add_shortcut (Gdk.KEY_l, lambda *w: self.addressbar.grab_focus (), meta = True)
        self.add_shortcut (Gdk.KEY_Left, lambda *w: self.back (), meta = True)
        self.add_shortcut (Gdk.KEY_Right, lambda *w: self.forward (), meta = True)
        self.add_shortcut (Gdk.KEY_Up, lambda *w: self.up (), meta = True)
        self.add_shortcut (Gdk.KEY_F1, lambda *w: self.new_tab ('filesystem'), meta = True)
        self.add_shortcut (Gdk.KEY_Menu, lambda *w: self.get_tab ().popup_menu ())

        self.add_shortcut (Gdk.KEY_1, lambda *w: self.notebook.set_current_page (0), meta = True)
        self.add_shortcut (Gdk.KEY_2, lambda *w: self.notebook.set_current_page (1), meta = True)
        self.add_shortcut (Gdk.KEY_3, lambda *w: self.notebook.set_current_page (2), meta = True)
        self.add_shortcut (Gdk.KEY_4, lambda *w: self.notebook.set_current_page (3), meta = True)
        self.add_shortcut (Gdk.KEY_5, lambda *w: self.notebook.set_current_page (4), meta = True)
        self.add_shortcut (Gdk.KEY_6, lambda *w: self.notebook.set_current_page (5), meta = True)
        self.add_shortcut (Gdk.KEY_7, lambda *w: self.notebook.set_current_page (6), meta = True)
        self.add_shortcut (Gdk.KEY_8, lambda *w: self.notebook.set_current_page (7), meta = True)
        self.add_shortcut (Gdk.KEY_9, lambda *w: self.notebook.set_current_page (8), meta = True)
        self.add_shortcut (Gdk.KEY_0, lambda *w: self.notebook.set_current_page (self.notebook.get_n_pages () - 1), meta = True)
        #self.add_shortcut (Gdk.KEY_Escape, lambda *w: self.search.set_search_mode (False) if self.search.get_search_mode () else None)
        del (self.shortcuts [Gdk.KEY_Escape])

        self.toolbar.up.connect ('clicked', lambda *w: self.up ())
        self.toolbar.home.connect ('clicked', lambda *w: self.home ())
        self.toolbar.back.connect ('clicked', lambda *w: self.back ())
        self.toolbar.forward.connect ('clicked', lambda *w: self.forward ())
    
    
    def add_service_provider (self, name, provider):
        self.service_providers [name] = provider
        self.provider.append_text (name)
    
    def close_current_tab (self, *w):
        p = self.notebook.get_nth_page (self.notebook.get_current_page ())
        if p is not None:
            p.destroy ()

    def get_tab (self):
        return self.notebook.get_nth_page (self.notebook.get_current_page ())

    def up (self):
        tab = self.get_tab ()
        tab.up ()

    def back (self):
        tab = self.get_tab ()
        tab.back ()

    def forward (self):
        tab = self.get_tab ()
        tab.forward ()

    def home (self):
        tab = self.get_tab ()
        tab.home ()

    def open (self, path):
        tab = self.get_tab ()
        tab.open (path)

    def new_tab (self, provider):
        tab = Tab (self, self.service_providers [provider])
        self.notebook.append_page (tab, Gtk.Label (provider))
        tab.iconview.grab_focus ()

    def hotkeys (self, window, event):
            #print (int (event.keyval))
            #print (Gdk.keyval_name (event.keyval), int (event.state))
            if int (event.state) == 20 or int (event.state) == 4 or int (event.state) == 8 or int (event.state) == 24:
                if event.keyval in self.meta_shortcuts:
                    self.meta_shortcuts [event.keyval] (self)
                    return True
    
            elif event.keyval in self.shortcuts:
                self.shortcuts [event.keyval] (self)
                return True

            elif Gdk.keyval_name (event.keyval).isalpha () and len (Gdk.keyval_name (event.keyval)) == 1:
                self.get_tab ().do_search (Gdk.keyval_name (event.keyval))
    

if __name__ == '__main__':
    w = Window ()
    w.main ()
