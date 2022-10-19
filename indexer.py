import os
import db

class Indexer:
	db = None
	def __init__ (self):
		self.db = DB ()
		
	def index (self, dirname):
		for root, dirs, files in os.walk(dirname):

