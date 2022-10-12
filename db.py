import MySQLdb as _mysql
import sql

# db = _mysql.connect("localhost","domino","remembermyname", "domino")
# db.query("""select * from files""")
# r=db.store_result()
# #print (r.fetch_row()[0][0])

# c=db.cursor()
# #max_price=5
# #c.execute("""insert into files (filename,md5,modified) values ("fil","jhakshahsdg", "2022-10-02 00:00:00");""")
# #db.commit()
# #print (c.fetchone())

# sql = "INSERT INTO files (filename, md5, modified) VALUES (%s, %s,%s)"
# val = ("filename.txt", "jashdjhagsd786", "2022-10-02 00:00:00")
# c.execute(sql, val)

# db.commit()
 
class DB:
	db = None
	def __init__ (self):
		self.db = _mysql.connect("localhost","domino","remembermyname", "domino")
		self.commit = self.db.commit

	def insert (self, table, cols, values):
		sql = f'INSERT INTO files (%s)' % ", ".join (cols) + " values ("
		for x in range (len (cols)):
			sql += "%s,"
		sql = sql [:-1] + ")"
		# print (sql)
		self.db.cursor ().execute (sql, values)

d = DB ()
d.insert ("files", ("filename", "md5", "modified"), ("filename.txt", "jashdjhagsd786", "2022-10-02 00:00:00"))
d.commit ()
