#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  cicada
#  2016-09-06

from gi.repository import Gtk

class Provider:
    default_path = None
    ui = None
    #ICON_SIZE = 64
    icon_theme = Gtk.IconTheme.get_default ()
    icons = icon_theme.list_icons ()

    def lookup_icon (self, name):
        ext = name.split ('.') [-1]
        #print (ext)
        if ext in self.icons:
            return self.icon_theme.load_icon (ext, self.ui.ICON_SIZE, Gtk.IconLookupFlags.GENERIC_FALLBACK)
        
        for icon in self.icons:
            if ext in icon:
                #print (ext, icon)
                return self.icon_theme.load_icon (icon, self.ui.ICON_SIZE, Gtk.IconLookupFlags.GENERIC_FALLBACK)
        
        return self.icon_theme.load_icon ('gtk-file', self.ui.ICON_SIZE, Gtk.IconLookupFlags.GENERIC_FALLBACK)
    
    
    def is_path (self, path):
        return False
    
    def get (self, path):
        return [None, None, None]
    
    
    def __init__ (self, ui = None):
        if ui:
            self.ui = ui
            #self.ui.store = ui.store
            #if hasattr (ui, 'ICON_SIZE'):
                #self.ICON_SIZE = self.ui.ICON_SIZE

    #def get_names (self, path = None):
        #return [None, None, None]

