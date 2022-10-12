import os
import db

class Indexer:
	db = None
	def __init__ (self):
		self.db = DB ()
		
	def index (self, dirname):
		
