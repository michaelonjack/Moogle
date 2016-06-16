import os
import cgi
import jinja2
import webapp2
import MySQLdb
from google.appengine.ext.webapp.util import run_wsgi_app
from helpers import get_config


def getDatabase():
	# Connect to database
	
	config = get_config()
	config.read('auth.ini')
	instance = config.get('credentials', 'instance')
	db = config.get('credentials', 'db')
	passw = config.get('credentials', 'pass')
	
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
		db = MySQLdb.connect(unix_socket='/cloudsql/' + instance, db=db, user='root', passwd=passw, charset='utf8')
	else:
		db = MySQLdb.connect(host='173.194.233.233', port=3306, db=db, user='root', passwd=passw, charset='utf8')
	
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
				('category', row[2]),
				('description', row[3]),
				('image', row[4]),
				('title', row[5])
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
				('category', row[4]),
				('description', row[5]),
				('image', row[6]),
				('title', row[7])
			])
		)
				
		
	db.close()
		
	return items
	
	
	
	
	
	
def getAllAuctionItems():

	db = getDatabase()
	cursor = db.cursor()
	cursor.execute('SELECT * FROM Auction_Items A INNER JOIN Items I on A.id=I.id;')
		
	items = []
	for row in cursor.fetchall():
		items.append( 
			dict([
				('id', row[0]),
				('end_date', row[1]),
				('reserve', row[2]),
				('quantity', row[4]),
				('category', row[5]),
				('description', row[6]),
				('image', row[7]),
				('title', row[8])
			])
		)
				
		
	db.close()
		
	return items

	
	




def insertIntoSaleItems(_id, price):
	db = getDatabase()
	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Sale_Items (id, price) VALUES (%s, %s)', (int(_id), float(price)))
	
	db.commit()
	db.close()



def getUserSelling(username):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT item_id from Users_Selling WHERE user=%s', (username))
	
	item_ids = []
	for row in cursor.fetchall():
		item_ids.append(row[0])
		
	db.close()
	return item_ids


def insertIntoUsersSelling(username, item_id):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('INSERT INTO Users_Selling (user, item_id) VALUES (%s, %s)', (username, int(item_id)))

	db.commit()
	db.close()
	
	
def getUserBuying(username):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT item_id from Users_Buying WHERE user=%s', (username))
	
	item_ids = []
	for row in cursor.fetchall():
		item_ids.append(row[0])
		
	db.close()
	return item_ids

def insertIntoUsersBuying(username, item_id):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Users_Buying WHERE user=%s AND item_id=%s', (username, int(item_id)))
	
	if len(cursor.fetchall()) > 0:
		cursor.execute('UPDATE Users_Buying SET quantity=quantity+1 WHERE user=%s AND item_id=%s', (username, int(item_id)))
	
	else:
		cursor.execute('INSERT INTO Users_Buying (user, item_id, quantity) VALUES (%s, %s, %s)', (username, int(item_id), 1))

	db.commit()
	db.close()






def getNewestItem():
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT max(id) from Items')
	
	db.close()
	return cursor.fetchone()[0]







def addItemToWatchlist(username, watchlist_name, item):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Watchlist_Items WHERE watchlist=%s AND item=%s AND owner=%s', (watchlist_name, int(item), username))
	
	if len(cursor.fetchall()) > 0:
		db.close()
		return
		
	else:
		cursor.execute('INSERT INTO Watchlist_Items (watchlist, item, owner) VALUES (%s, %s, %s)', (watchlist_name, int(item), username))
		
	db.commit()
	db.close()
	
	
	

def insertWatchlistForUser(username, watchlist_name):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Watchlists WHERE owner=%s AND name=%s', (username, watchlist_name))
	if len(cursor.fetchall()) > 0:
		db.close()
		return False
	
	cursor.execute('INSERT INTO Watchlists (name, owner) VALUES (%s, %s)', (watchlist_name, username))
	
	db.commit()
	db.close()
	return True



def getWatchlistsForUser(username):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT name FROM Watchlists WHERE owner=%s', (username))
	
	names = [] 
	for row in cursor.fetchall():
		names.append(row[0])
		
	db.close()
	return names



def getWatchlistItems(username, name):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT item FROM Watchlist_Items WHERE watchlist=%s AND owner=%s', (name, username))
	
	item_ids = []
	for row in cursor.fetchall():
		item_ids.append(row[0])
		
	db.close()
	return item_ids
	










def insertIntoAuctionItems(_id, end_date, reserve):
	db = getDatabase()
	cursor = db.cursor()
    # Note that the only format specifier supported is %s
	cursor.execute('INSERT INTO Auction_Items (id, end_date, reserve) VALUES (%s, %s, %s)', (int(_id), end_date, float(reserve)))
	
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
	
	




def insertBid(username, item, amount):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Bids WHERE username=%s AND item=%s', (username, int(item)))
	
	# A bid for this item already exists, update the amount
	if len(cursor.fetchall()) > 0:
		cursor.execute('UPDATE Bids SET amount=%s, username=%s WHERE item=%s', (float(amount), username, int(item)))
	# No bids for this item yet, enter it into the table
	else:
		cursor.execute('INSERT INTO Bids (username,item,amount) VALUES (%s,%s,%s)', (username, int(item), float(amount)))
	
	db.commit()
	db.close()
	




def getSellerOfItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Users_Selling WHERE item_id=%s', (int(item_id),))
	
	row = cursor.fetchone()
	if row is not None:
		seller = row[0]
		
		db.close()
		return seller
	
	db.close()
	return None





def getBidForItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('SELECT * FROM Bids WHERE item=%s', (int(item_id),))
	
	row = cursor.fetchone()
	if row is not None:
		bid = dict([
			('bidder', row[0]),
			('item_id', row[1]),
			('amount', row[2]),
			('time', row[3]),
			('id', row[4])
		])
		db.close()
		return bid
	
	db.close()
	return None





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
	
	




def insertIntoUserAddress(username, street, zipcode):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('INSERT INTO User_Address (username, street, zipcode) VALUES (%s, %s, %s)', (username,street,zipcode))
	
	db.commit()
	db.close()
	






def insertIntoUserPhoneNumber(username, number):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('INSERT INTO User_PhoneNumber (username, phone_number) VALUES (%s, %s)', (username,number))
	
	db.commit()
	db.close()
	




def insertIntoUserCreditCard(username, number, card_type, date):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('INSERT INTO User_CreditCard (username, number, type, expiration_date) VALUES (%s, %s, %s, %s)', (username,number,card_type,date))
	
	db.commit()
	db.close()
	return True
	





def findCreditCard(number, card_type):
	db = getDatabase()
	cursor= db.cursor()
	cursor.execute('SELECT * FROM User_CreditCard WHERE number=%s AND type=%s', (number, card_type))
	
	if len(cursor.fetchall()):
		db.close()
		return False
		
	else:
		db.close()
		return True









def insertIntoZipcodeArea(zipcode, city, state):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Zipcodes_Areas WHERE zipcode='" + zipcode + "'")

	# Zipcode already exists
	if len(cursor.fetchall()) > 0:
		db.close()
		return False
	
	
	cursor.execute("INSERT INTO Zipcodes_Areas (zipcode, city, state) VALUES (%s, %s, %s)", (zipcode,city,state))
	
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
					('category', row[2]),
					('description', row[3]),
					('image', row[4]),
					('title', row[5])
				])
			)
				
	# close connect	
	db.close()
		
	return items


def getUser(username):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Users U INNER JOIN User_Address A on U.username=A.username AND U.username=%s INNER JOIN User_PhoneNumber P on U.username=P.username INNER JOIN Zipcodes_Areas Z on Z.zipcode=A.zipcode INNER JOIN User_CreditCard C on C.username=U.username", (username))
	
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
					('birth_date', str(row[7])),
					('street', row[9]),
					('zipcode', row[10]),
					('phone_number', row[12]),
					('city', row[14]),
					('state', row[15]),
					('card_number', row[17]),
					('card_type', row[18]),
					('card_expr', str(row[19]))
				])
		db.close
		return user
				
	else:
		cursor.execute("SELECT * FROM Users WHERE username='" + username + "'")
	
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
						('birth_date', str(row[7]))
					])
		db.close
		return user
		
	return None
	
				
				
def getItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Items WHERE id=%s", (item_id))
	
	row = cursor.fetchone()
	item = dict([
				('id', row[0]),
				('quantity', row[1]),
				('category', row[2]),
				('description', row[3]),
				('image', row[4]),
				('title', row[5])
			])	
		
	db.close()
		
	return item

def getSaleItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Sale_Items S INNER JOIN Items I on S.id=I.id AND S.id='" + str(item_id) + "'")
	
	item = []
	for row in cursor.fetchall():
		item.append( 
			dict([
				('id', row[0]),
				('price', row[1]),
				('quantity', row[3]),
				('category', row[4]),
				('description', row[5]),
				('image', row[6]),
				('title', row[7])
			])
		)
				
		
	db.close()
		
	return item
	

def getAuctionItem(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Auction_Items A INNER JOIN Items I on A.id=I.id AND A.id='" + str(item_id) + "'")
	
	item = []
	for row in cursor.fetchall():
		item.append( 
			dict([
				('id', row[0]),
				('end_date', row[1]),
				('reserve', row[2]),
				('quantity', row[4]),
				('category', row[5]),
				('description', row[6]),
				('image', row[7]),
				('title', row[8])
			])
		)
				
		
	db.close()
		
	return item
	






def getItemSeller(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute('SELECT user FROM Users_Selling WHERE item_id='+str(item_id))
	
	row = cursor.fetchone()
	user = row[0]
	return user

	




def decreaseItemQuantity(item_id):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute('SELECT quantity FROM Items WHERE id=%s', (int(item_id),))
	quantity = cursor.fetchone()[0]
	
	# Check to make sure there is more than one of the item, otherwise delete it from the table
	if quantity > 1:
		cursor.execute('UPDATE Items SET quantity=quantity-1 WHERE id=%s', (int(item_id),))
	else:
		cursor.execute('DELETE FROM Items WHERE id=%s', (int(item_id),))

	db.commit()
	db.close()









def makeHerdMember(username):
	db = getDatabase()
	cursor = db.cursor()
	
	cursor.execute('UPDATE Users SET herd_member=1 WHERE username=%s', (username))

	db.commit()
	db.close()








def login(username, password):
	db = getDatabase()
	cursor = db.cursor()
	cursor.execute("SELECT * FROM Users WHERE username='" + username + "' AND password='" + password + "'")
	
	row = cursor.fetchone()
	if row is not None:
		return row[5] #username
		
	return None
	


	
