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
# getAllSaleItems
# insertIntoItems
# getAllCategories
# getAllItemsFromCategory
######################################################################################



def getDatabase():
	# Connect to database
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
		db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='moogle', user='root', passwd='moogle', charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db='moogle', user='root', passwd='moogle', charset='utf8')
	
	return db


# Func to get all items from the database 
def getAllItems():
		
	db = getDatabase()
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

	db = getDatabase()
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



def insertIntoSaleItems(_id, price):
	db = getDatabase()
	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Sale_Items (id, price) VALUES (%s, %s)', (_id, price))
	
	db.commit()
	db.close()


def insertIntoAuctionItems(_id, end_date, reserve):
	db = getDatabase()
	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Auction_Items (id, end_date, reserve) VALUES (%s, %s, %s)', (_id, end_date, reserve))
	
	db.commit()
	db.close()


# Func to insert an item into the database
def insertIntoItems(quantity, category, description, image, title):

	db = getDatabase()
	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Items (quantity, category, description, image, title) VALUES (%s, %s, %s, %s, %s)', (int(quantity), category, description, image, title))
	
	db.commit()
	db.close()
	
	
	
def insertIntoUsers(name, email, income, gender, username, password, birthdate):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Users WHERE username='" + username + "'")

	# User already exists
	if len(cursor.fetchall()) > 0:
		return False
		
	else:
		cursor.execute('INSERT INTO Users (name, email, herd_member, income, gender, username, password, birth_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (name, email, 0, (float(income)), gender, username, password, birthdate))
	
	db.commit()
	db.close()
	return True


# Func to get all categories from the database
def getAllCategories():

	db = getDatabase()
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
	
	
# Retrieves all categories that do not have children but are descendants of 'category'
def getBaseCategories(category, allCategories):
	
	baseCats = []
	childCats = getChildCategories(category, allCategories)
	if not childCats:
		baseCats.append(category)
		return baseCats
	else:
		for c in childCats:
			baseCats = baseCats + getBaseCategories(c, allCategories)	
			
	return baseCats
	
	

# Returns a list of all categories that are children of 'category'
def getChildCategories(category, allCategories):
	children = []
	for c in allCategories:
		if c['parent']==category:
			children.append(c['name'])
			
	return children
		
	

def getAllItemsFromCategory(category, allCategories):

	db = getDatabase()
	cursor = db.cursor()
	
	allBaseCategories = getBaseCategories(category, allCategories)
	
	# load everything into a dictionary
	items = []
	for b in allBaseCategories:
		cursor.execute("""SELECT * FROM Items WHERE category='""" + b + "'")
	
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
				
	# close connect	
	db.close()
		
	return items
	


def getSaleItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Sale_Items S INNER JOIN Items I on S.id=I.id AND S.id='" + item_id + "'")
	
	item = []
	for row in cursor.fetchall():
		item.append( 
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
		
	return item
	

def getAuctionItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Auction_Items A INNER JOIN Items I on A.id=I.id AND A.id='" + item_id + "'")
	
	item = []
	for row in cursor.fetchall():
		item.append( 
			dict([
				('id', row[0]),
				('end_date', row[1]),
				('reserve', row[2]),
				('max_bid', row[3]),
				('quantity', row[5]),
				('category', cgi.escape(row[6])),
				('description', cgi.escape(row[7])),
				('image', cgi.escape(row[8])),
				('title', cgi.escape(row[9]))
			])
		)
				
		
	db.close()
		
	return item
	
	
	
def login(username, password):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Users WHERE username='" + username + "' AND password='" + password + "'")
	
	row = cursor.fetchone()
	if row is not None:
		user = dict([
			('name', row[0]),
			('email', row[1]),
			('herd_member', row[2]),
			('income', row[3]),
			('gender', row[4]),
			('username', row[5]),
			('password', row[6]),
			#('birth_date', row[7])
		])
		return user
		
	return None
	


	
