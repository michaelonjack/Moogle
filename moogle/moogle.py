import os
import cgi
import jinja2
import webapp2
import MySQLdb
import urllib
import random
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.api import mail
from webapp2_extras import sessions
from databasefunc import *


template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), extensions=['jinja2.ext.loopcontrols'],
        autoescape = True) #Jinja will now autoescape all html

def do_urlescape(value):
    return urllib.quote(value.encode('utf8'))
jinja_env.globals['urlencode'] = do_urlescape
        
# THREE FUNCTIONS FOR RENDERING BASIC TEMPLATES
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
    
	def render_str(self,template, **kw):
		t = jinja_env.get_template(template)
		return t.render(kw)

	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))
	
	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()
    


######################################################################################################################



# Home page
class MainPage(Handler):
	def get(self):
		categories = getAllCategories()
		items = getAllItems()
		
		# Randomize the items to be shown
		random.shuffle(items)
		
		self.render("category.html", currentCategory='All', items=items, categories=categories, user=self.session.get('user'))



class CategoryPage(Handler):
	def get(self):
		selectedCategory = self.request.get("cat")
		categories = getAllCategories()
		items = getAllItemsFromCategory(selectedCategory, categories)
		
		# Randomize the items to be shown
		random.shuffle(items)
		
		self.render("category.html", currentCategory=selectedCategory, items=items, categories=categories, user=self.session.get('user'))



		

class ItemPage(Handler):
	def get(self):
		item_id = str(self.request.get("id"))
		user = self.session.get('user')
		sale_item = getSaleItem(item_id)
		categories = getAllCategories()
		
		# Check if the selected item was a sale item or auction item
		if sale_item:
			similar_items = getAllItemsFromCategory(sale_item[0]['category'], categories)
			
			if user:
				user['herd_member'] = int(user['herd_member'])
				if user['herd_member'] == 1:
					sale_item[0]['price'] = float(sale_item[0]['price']) * .9
			
			# Randomize the items to be shown
			random.shuffle(similar_items)
			
			self.render("sale_item.html", item=sale_item[0], related_items=similar_items, user=user)
		
		else:
			auction_item = getAuctionItem(item_id)
			similar_items = getAllItemsFromCategory(auction_item[0]['category'], categories)
			max_bid = getBidForItem(item_id)
			seller = getSellerOfItem(item_id)
			
			# Randomize the items to be shown
			random.shuffle(similar_items)
			
			self.render("auction_item.html", item=auction_item[0], related_items=similar_items, user=self.session.get('user'), max_bid=max_bid, seller=seller)













class LoginPage(Handler):
	def get(self):
		self.render("login.html", error_msg="")
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		
		current_user = login(username, password)
		
		if current_user is not None:
			self.session['user'] = getUser(current_user)
			self.redirect("/")
		else:
			self.render("login.html", error_msg="Username/password combination not found.")






class LogoutPage(Handler):
	def get(self):
		self.session['user'] = None
		self.redirect("/")







class SignupPage(Handler):
	def get(self):
		self.render("signup.html",msg="")
	def post(self):
		name = self.request.get('fullname')
		email = self.request.get('email')
		birthdate = self.request.get('year') + '-' + self.request.get('month') + '-' + self.request.get('day')
		username = self.request.get('username')
		password = self.request.get('password')
		street = self.request.get('street')
		city = self.request.get('city')
		state = self.request.get('state')
		zipcode = self.request.get('zipcode')
		phone = self.request.get('phone')
		card_num = self.request.get('card_num')
		card_type = self.request.get('card_type')
		card_expr_date = self.request.get('card_year') + '-' + self.request.get('card_month') + '-01'
		income = self.request.get('income')
		gender = self.request.get('gender')
		
		if not username or not password or not email or not birthdate or not name or not street or not city or not state or not zipcode or not phone or not card_num or not card_type or not income or not gender:
			self.render("signup.html",msg="DID NOT FILL IN ALL REQUIRED FIELDS")
		
		elif not findCreditCard(card_num, card_type):
			self.render("signup.html",msg="CREDIT CARD ALREADY IN USE")
		
		elif insertIntoUsers(name, email, float(income), gender, username, password, birthdate):
			
			# insert into zipcodes database
			insertIntoZipcodeArea(zipcode, city, state)
			
			# insert into address database
			insertIntoUserAddress(username, street, zipcode)
			
			# insert into credit card database
			insertIntoUserCreditCard(username, card_num, card_type, card_expr_date)
			
			# insert into phone number database
			insertIntoUserPhoneNumber(username, phone)
			
			# Send email
			message = "Hi " + name + "!\n\n Welcome to Moogle. Hope you have a lot of fun!\nYour username is " + username + "\n\nhttp://moogle-store.appspot.com"
			mail.send_mail(sender="mooglethestore@gmail.com",to=email,subject="Hi from Moogle!",body=message)
			self.redirect("/")
		else:
			self.render("signup.html",msg="USERNAME ALREADY IN USE")










# Action to be performed when a user enters a search query
class SearchStoreAction(Handler):
	def post(self):
		query = self.request.get('query')
		category = self.request.get('cat')
		allCategories = getAllCategories()
		
		if not category:
			allItems = getAllItems()
		else:
			allItems = getAllItemsFromCategory(category, allCategories)
		
		displayedItems = []
		for item in allItems:
			if query.lower() in item['title'].lower():
				displayedItems.append(item)
		
		if not category:		
			self.render("category.html", currentCategory='All', items=displayedItems, categories=allCategories, user=self.session.get('user'))
		
		else:
			self.render("category.html", currentCategory=category, items=displayedItems, categories=allCategories, user=self.session.get('user'))













class VerifyBidder(Handler):
	def get(self):
		seller = self.request.get('seller')
		item_id = self.request.get('item')
		bid = self.request.get('bid')
		
		user = self.session.get('user')
		
		if not user:
			self.redirect('/login')
		else:
			self.render('verifybidder.html', error_msg="", username=user['username'], user=seller, item=item_id, bid=bid)
		
			
# Action to be performed when a user places a bid
class PlaceBidAction(Handler):
	def post(self):
	
		seller = self.request.get('user')
		item_id = int(self.request.get('item'))
		bidder = self.session.get('user')
		password = self.request.get('password')
		
		current_max_bid = getBidForItem(item_id)
		if not current_max_bid:
			current_max_bid = 0.0
		else:
			current_max_bid = float(current_max_bid['amount'])
		
		bid = self.request.get('bid')
		if not bid:
			bid = 0
		else:
			bid = float(bid)

		if password == bidder['password']:
			# get item from database
			item = getAuctionItem(item_id)
	
			if not bid:
				self.render('message.html', message="No bid entered.")
			elif bid <= current_max_bid:
				self.render('message.html', message="Bid must be higher than current bid.")
			elif bidder['username'] == seller:
				self.render('message.html', message="Seller cannot bid on their own items.")
			else:
				insertBid(bidder['username'], item_id, bid)
				
				self.redirect("/item?id=" + str(item_id))

		else:
			self.render('verifybidder.html', error_msg="Incorrect password", username=bidder['username'], user=seller, item=item_id, bid=bid)










class VerifyBuyer(Handler):
	def get(self):
		item_id = self.request.get('item')
		user = self.session.get('user')
		
		if not user:
			self.redirect('/login')
		else:
			self.render('verifybuyer.html', error_msg="", username=user['username'], item=item_id)
			
class VerifyPurchase(Handler):
	def get(self):
		item_id = self.request.get('item')
		user = self.session.get('user')
		item = getSaleItem(item_id)[0]
		
		if not user:
			self.redirect('/login')
		else:
			if user['herd_member']==1:
				item['price'] = item['price'] * .9
			self.render('verifypurchase.html', buyer=user, item=item)
			
# Action to be performed when user buys an item
class BuyItemAction(Handler):
	def post(self):
		item_id = self.request.get('item')
		user = self.session.get('user')
		password = self.request.get('password')
		item = getSaleItem(item_id)[0]
		
		if password == user['password']:
			insertIntoUsersBuying(user['username'], item_id)
			decreaseItemQuantity(item_id)
			
			if user['herd_member'] == 1:
				item['price'] = item['price'] * .9
			
			# Send email to buyer to confirm purchase
			message = "Hi " + user['name'] + ".\n\nThanks for buying " + item['title'] + ". We'll be sure to ship it out eventually or something.\n$" + str(item['price']) + " will be deducted from your card soon.\n\nThanks from Moogle!"
			mail.send_mail(sender="mooglethestore@gmail.com",to=user['email'],subject="Your Order From Moogle",body=message)
			
			self.redirect("/item?id="+ str(item['id']))
		
		else:
			self.render('verifybuyer.html', error_msg="Incorrect password", username=user['username'], item=item_id)









class VerifySeller(Handler):
	def get(self):
		user = self.session.get('user')
		
		title = self.request.get('title')
		category = self.request.get('category')
		description = self.request.get('description')
		image = self.request.get('image')
		
		reserve = self.request.get('reserve')
		end_date = '2016-' + self.request.get('month') + '-' + self.request.get('day')
		
		params = dict([
					('title', urllib.quote(title.encode('utf8'))),
					('category', urllib.quote(category.encode('utf8'))),
					('description', urllib.quote(description.encode('utf8'))),
					('image', urllib.quote(image.encode('utf8'))),
					('reserve', reserve),
					('end_date', end_date)
				])
		
		if not user:
			self.redirect('/login')
		else:
			if not title or not category or not description or not image or not end_date:
				self.render("auction_post.html", msg="DID NOT FILL IN ALL REQUIRED FIELDS", categories=getAllCategories())
			else:
				self.render('verifyseller.html', error_msg="", username=user['username'], params=params)


class SellItemAction(Handler):
	def post(self):
		user = self.session.get('user')
		
		title = urllib.unquote(self.request.get('title').decode('utf8'))
		category = urllib.unquote(self.request.get('category').decode('utf8'))
		description = urllib.unquote(self.request.get('description').decode('utf8'))
		image = urllib.unquote(self.request.get('image').decode('utf8'))
		quantity=1
		
		reserve = self.request.get('reserve')
		if not reserve:
			reserve=0.0
		end_date = self.request.get('end_date')
		
		password = self.request.get('password')
		
		if password == user['password']:
			
			insertIntoItems(quantity, category, description, image, title)
			
			item_id = getNewestItem()
					
			insertIntoUsersSelling(user['username'], item_id)
			insertIntoAuctionItems(item_id, end_date, reserve)
			
			self.redirect("/item?id="+str(item_id))
		else:
			params = dict([
						('title', urllib.quote(title.encode('utf8'))),
						('category', urllib.quote(category.encode('utf8'))),
						('description', urllib.quote(description.encode('utf8'))),
						('image', urllib.quote(image.encode('utf8'))),
						('reserve', reserve),
						('end_date', end_date)
					])
			
			self.render('verifyseller.html', error_msg="Incorrect password", username=user['username'], params=params)
		
		
		

class SellItemPage(Handler):
	def get(self):
		self.render("auction_post.html", msg="", categories=getAllCategories())








class MessagePage(Handler):
	def get(self):
		title = self.request.get('title')
		message = self.request.get('message')

		self.render("message.html", title=title, message=message)







class HerdMember(Handler):
	def get(self):
		self.render("herdmember.html", user=self.session.get('user'))
	def post(self):
		if self.session.get('user') is None:
			self.redirect('/login')
		else:
		
			user = self.session.get('user')
		
			message = "Hi " + user['name'] + ".\n\nThanks for becoming a herd member\n$60 will be deducted from your card soon.\n\nThanks from Moogle!"
			mail.send_mail(sender="mooglethestore@gmail.com",to=user['email'],subject="Your Order From Moogle",body=message)
			
			
			makeHerdMember(user['username'])
			self.session['user'] = getUser(user['username'])
			
			self.render('confirmherdmember.html')
		





class UserBuyingSelling(Handler):
	def get(self):
		buying = int(self.request.get('buying'))
		user = self.session['user']
		
		if buying:
			item_ids = getUserBuying(user['username'])
				
		else:
			item_ids = getUserSelling(user['username'])
			
		
		items = []
		for _id in item_ids:
			items.append(getItem(_id))
		
		self.render('itemdisplay.html', user=user, items=items, _type=buying, name="")
		

class MyAccountPage(Handler):
	def get(self):
		user = self.session['user']
		
		if user is not None:
			self.render('user_account.html', user=user)
			
		else:
			self.redirect('/login')








class AddToWatchlistPage(Handler):
	def get(self):
		user = self.session['user']
		item = self.request.get('item')
		
		if user is None:
			self.redirect('/login')
		
		else:
			watchlists = getWatchlistsForUser(user['username'])
			self.render('addtowatchlist.html', user=user, watchlists=watchlists, item=item)
			
	def post(self):
		user = self.session['user']
		name = self.request.get('name')
		item = self.request.get('item')
		
		addItemToWatchlist(user['username'], name, item)
		
		self.redirect('/item?id='+item)

class UserWatchlistsPage(Handler):
	def get(self):
		user = self.session['user']
		name = self.request.get('name')
		
		if not name:
			watchlists = getWatchlistsForUser(user['username'])
			self.render('choosewatchlist.html', user=user, watchlists=watchlists, error_msg="")

		else:
			item_ids = getWatchlistItems(user['username'], name)
			items = []
			for _id in item_ids:
				items.append(getItem(_id))
			
			self.render('itemdisplay.html', user=user, items=items, _type=2, name=name)
			
	def post(self):
		user = self.session['user']
		name = self.request.get('name')
			
		if not name:
			watchlists = getWatchlistsForUser(user['username'])
			self.render('choosewatchlist.html', user=user, watchlists=watchlists, error_msg="DID NOT ENTER A NAME")
			
		elif insertWatchlistForUser(user['username'], name):
			watchlists = getWatchlistsForUser(user['username'])
			self.render('choosewatchlist.html', user=user, watchlists=watchlists, error_msg="")

		else:
			watchlists = getWatchlistsForUser(user['username'])
			self.render('choosewatchlist.html', user=user, watchlists=watchlists, error_msg="WATCHLIST NAME ALREADY EXISTS")





class TestPagePost(Handler):
	def get(self):
		self.render("testing-post.html")

	def post(self):
		quantity = self.request.get('quantity')
		category = self.request.get('category')
		description = self.request.get('description')
		image = self.request.get('image')
		title = self.request.get('title')

		insertIntoItems(quantity, category, description, image, title)

		self.redirect("/testpost")
		









######################################################################################################################

# Map the class handlers to their URLs


config = {}
config['webapp2_extras.sessions'] = {
	'secret_key': 'my_secret_key',
}
application = webapp2.WSGIApplication([
	('/', MainPage),
	(r'/category.*', CategoryPage),
	(r'/item.*', ItemPage),
	('/login', LoginPage),
	('/logout', LogoutPage),
	('/signup', SignupPage),
	('/search', SearchStoreAction),
	('/placebid', PlaceBidAction),
	('/verifybid', VerifyBidder),
	('/buyitem', BuyItemAction),
	('/verifybuy', VerifyBuyer),
	('/verifypurchase', VerifyPurchase),
	('/sellitem', SellItemPage),
	('/sellitemaction', SellItemAction),
	('/verifyseller', VerifySeller),
	('/message', MessagePage),
	('/herdmembership', HerdMember),
	('/myaccount', MyAccountPage),
	('/myaccount/buyingselling', UserBuyingSelling),
	('/myaccount/watchlists', UserWatchlistsPage),
	('/addtowatchlist', AddToWatchlistPage),
	('/testpost', TestPagePost),
	], debug=True, config=config)
	
	
	
	
	
	
	
	
	
	
	
	

