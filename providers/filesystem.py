#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  cicada
#  2016-09-06

import pathlib
import sys, os
from gi.repository import Gtk
from providers.provider import Provider
from enum import Enum

class Sort (Enum):
#    none = 0
    name = 1
    date = 2
    size = 3

def get_key_name (a):
    return a [1].lower ()

def get_key_date (a):
    stat = os.stat (a [2])
    return stat.st_mtime

def get_key_size (a):
    stat = os.stat (a [2])
    return stat.st_size

class Filesystem (Provider):
    icon_theme = Gtk.IconTheme.get_default ()
    icons = icon_theme.list_icons ()
    default_path = os.environ ['HOME']
    sort = Sort.date
    sort_reverse = True
    
    config = ['sort', 'sort_reverse']
    
    def get_sort_reverse (self):
        return self.sort_reverse
    
    def get_sort (self):
        return self.sort.name
    
    def set_sort_reverse (self, reverse):
        self.sort_reverse = reverse

    def set_sort (self, sort):
        sort = sort.lower ()
        if '_' in sort:
            sort = sort.replace ('_', '')
        self.sort = Sort [sort]

    def get_sort_types (self):
        sort = []
        for a in dir (Sort):
            if a [0] != '_':
                sort.append (a)
        return sort
        
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
    
    def get (self, path):
        if not os.path.exists (path):
            return None
        
        p = pathlib.Path (path)
        files = list (p.glob ('*'))
        
        folders = []
        fills = []
        
        for e in files:
            f = str (e)
            #print (f, e.is_dir ())
            basename = os.path.basename (f)
            if e.is_dir ():
                if not basename [0] == '.':
                    if len (basename) > 12:
                        basename = basename [:10] + '...'
                    folders.append ([self.lookup_icon ('folder'), basename, f])
            else:
                if not basename [0] == '.':
                    icon = self.lookup_icon (basename)
                    if len (basename) > 12:
                        basename = basename [:10] + '...'
                    fills.append ([icon, basename, f])
        
        #print (self.sort)

        if isinstance (self.sort, str):
            #print (self.sort)
            if hasattr (Sort, self.sort):
                self.sort = getattr (Sort, self.sort)

        if self.sort == Sort.name:
            folders.sort (key = get_key_name, reverse = self.sort_reverse)
            fills.sort (key = get_key_name, reverse = self.sort_reverse)
        elif self.sort == Sort.date:
            folders.sort (key = get_key_date, reverse = self.sort_reverse)
            fills.sort (key = get_key_date, reverse = self.sort_reverse)            
        elif self.sort == Sort.size:
            folders.sort (key = get_key_size, reverse = self.sort_reverse)
            fills.sort (key = get_key_size, reverse = self.sort_reverse)            
        return folders + fills

    def is_path (self, path):
        return os.path.isdir (path)
    
    def open (self, path):
        os.system ('xdg-open \"{}\"'.format (path))
