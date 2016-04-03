import os
import cgi
import jinja2
import webapp2
import MySQLdb
from google.appengine.ext.webapp.util import run_wsgi_app

# Name of the database to connect to "APP-ID:DB-NAME
_INSTANCE_NAME = 'moogle-store:moogle-db1'

############################## FUNCS #################################################
# getAllItems
# insertIntoItems
# getAllCategories
######################################################################################




# Func to get all items from the database 
def getAllItems():

	# Connect to database
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
		db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='moogle', user='root', passwd='moogle', charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db='moogle', user='root', passwd='moogle', charset='utf8')
		
	cursor = db.cursor()
	cursor.execute('SELECT * FROM Items')
		
	items = []
	for row in cursor.fetchall():
		items.append( 
			dict([
				('id', row[0]),
				('quantity', row[1]),
				('category', cgi.escape(row[2])),
				('description', cgi.escape(row[3])),
				('image', cgi.escape(row[4])),
				('title', cgi.escape(row[5]))
			])
		)
				
		
	db.close()
		
	return items
	






def getAllSaleItems():

	# Connect to database
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
		db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='moogle', user='root', passwd='moogle', charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db='moogle', user='root', passwd='moogle', charset='utf8')
		
	cursor = db.cursor()
	cursor.execute('SELECT * FROM Sale_Items S INNER JOIN Items I on S.id=I.id;')
		
	items = []
	for row in cursor.fetchall():
		items.append( 
			dict([
				('id', row[0]),
				('price', row[1]),
				('quantity', row[3]),
				('category', cgi.escape(row[4])),
				('description', cgi.escape(row[5])),
				('image', cgi.escape(row[6])),
				('title', cgi.escape(row[7]))
			])
		)
				
		
	db.close()
		
	return items





# Func to insert an item into the database
def insertIntoItems(quantity, category, description, image, title):

	# Connect to database
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
		db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='moogle', user='root', passwd='moogle', charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db='moogle', user='root', passwd='moogle', charset='utf8')

	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Items (quantity, category, description, image, title) VALUES (%s, %s, %s, %s, %s)', (int(quantity), category, description, image, title))
	
	db.commit()
	db.close()
	
	
	





# Func to get all categories from the database
def getAllCategories():

	# Connect to database
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
		db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='moogle', user='root', passwd='moogle', charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db='moogle', user='root', passwd='moogle', charset='utf8')
	
	# Execute the query
	cursor = db.cursor()
	cursor.execute('SELECT * FROM Categories')
	
	# load everything into a dictionary
	categories = []
	for row in cursor.fetchall():
		categories.append( 
			dict([
				('name', row[0]),
				('parent', row[1])
			])
		)
				
	# close connect	
	db.close()
		
	return categories
	
	
	
