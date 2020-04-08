#!/usr/bin/env python3

import ZODB, ZODB.FileStorage
from pathlib import Path
import persistent
import transaction
import BTrees.OOBTree
import os, sys
if __name__ == '__main__':
    from provider import Provider
else:
    from providers.provider import Provider

class Storage (persistent.Persistent):
    default_database = os.path.expanduser ("~/.config/leila/tags")
    commit = transaction.commit
    abort = transaction.abort

    create_node = BTrees.OOBTree.BTree
    root = None

    def __init__ (self):
        if not os.path.exists (self.default_database):
            os.makedirs (os.path.dirname (self.default_database), exist_ok = True)
            
        self.zodb_storage = ZODB.FileStorage.FileStorage (self.default_database)
        self.zodb = ZODB.DB (self.zodb_storage)
        
    def open (self, node = None):
        self.zodb_connection = self.zodb.open ()
        self.root = self.zodb_connection.root ()

        if node:
            if not node in self.root:
                self.root [node] = BTrees.OOBTree.BTree ()
            self.root = self.root [node]
        return self.root

    def close (self):
        self.zodb_connection.close ()
        self.zodb.close ()
        self.zodb_storage.close ()

    def set (self, *args):
        path = self.root
        for x in range (len (args) - 1):
            if not path.has_key (args [x]):
                path [args [x]] = BTrees.OOBTree.BTree ()
            path = path [args [x]]

        path [args [-1]] = args [-1]

    def link (self, key, value):
        self.root [key] = self.create_node ()
        self.root [key][value] = self.root [value]

    def get (self, *args, recursive = True):
        path = self.root
        for x in range (len (args)):
            if not path.has_key (args [x]):
                return None
            path = path [args [x]]

        if type (path) != BTrees.OOBTree.OOBTree:
            if recursive:
                return [path]
            else:
                return path
        
        items = []
        for i in path:
            items .append (i)
        
        if not recursive:
            return items [0]
        else:
            return items

    def print_db (self, node = None, level = 0, maxdepth = 5):
        if node == None:
            node = self.root
            
        for i in node:
            print ("--" * level, i)
            #print (i, type (node [i]))
            if level > maxdepth:
                break
            if type (node [i]) == BTrees.OOBTree.OOBTree:
                self.print_db (node [i], level + 1)
            
    def get_nodes (self, root):
        if root is None:
            root = self.root
        
        ret = []
        for r in root:
            ret.append ((r, root [r]))
        
        return ret


def get_files (dirname):
    files = []

    path = Path (dirname)
    for a in path.iterdir ():
        if a.is_file ():
            files.append (str (a))
        elif a.is_dir ():
            files += get_files (str (a))
    
    return files
    
def generate_tags (dirname):
    files = get_files (dirname)
    s = Storage ()
    s.open ('tags')
    
    for f in files:
        b = os.path.basename (f)
        b = b [:b.find ('.')]
        s.set (b, f)
        v = b.split ()
        for a in v:
            if a != '' and len (a) > 1:
                #print (a, len (a))
                s.link (a, b)
                s.link (b, a)
        
    s.commit ()
    s.close ()

def generate_database (dirname):
    files = get_files (dirname)
    s = Storage ()
    s.open ('videos')
    
    for f in files:
        print (f)
        path = []
        for a in f.split ('/'):
            if a != '':
                path.append (a)
        path.append (f)
        s.set (*path)

    s.commit ()
    s.close ()
    
if __name__ == '__main__':
    #generate_tags (sys.argv [1])
    s = Storage ()
    s.open ('videos')
    s.print_db ()
    #generate_database (sys.argv [1])
    pass

class Videos (Provider):
    default_path = '/'
    
    def __init__ (self, ui = None):
        self.ui = ui
        self.storage = Storage ()
        self.storage.open (None)
    
    def is_path (self, path):
        # if self.
        return isinstance (path, BTrees.OOBTree.OOBTree)
    
    def on_delete (self):
        self.storage.close ()
        print ('bye')

    def get (self, path):
        dirname = self.storage.root
        if path is not None and path != '/':
            for a in path.split ('/'):
                if a != '':
                    if a in dirname:
                        dirname = dirname [a]
        files = []
        for a in dirname:
            if self.is_path (dirname [a]):
                files.append ([self.lookup_icon ('folder'), a, path + '/' + a])
            else:
                files.append ([self.lookup_icon ('video'), a, path + '/' + a])
        
        self.storage.print_db ()
        return files
