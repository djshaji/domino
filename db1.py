import MySQLdb as _mysql
db = _mysql.connect("localhost","domino","remembermyname", "domino")
db.query("""select * from files""")
r=db.store_result()
#print (r.fetch_row()[0][0])

c=db.cursor()
#max_price=5
#c.execute("""insert into files (filename,md5,modified) values ("fil","jhakshahsdg", "2022-10-02 00:00:00");""")
#db.commit()
#print (c.fetchone())

sql = "INSERT INTO files (filename, md5, modified) VALUES (%s, %s,%s)"
val = ("filename.txt", "jashdjhagsd786", "2022-10-02 00:00:00")
c.execute(sql, val)

db.commit()
 
class DB:
	db = None
	def __init__ ():
		db = _mysql.connect("localhost","domino","remembermyname", "domino")

	def insert (table, cols, values):
		sql = "insert into %s (%s" % (table, cols [0])
		i = 1
		values = "%s"
		for i in range (1, len (cols)):
			sql += cols 
