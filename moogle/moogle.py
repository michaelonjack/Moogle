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
		sale_item = getSaleItem(item_id)
		categories = getAllCategories()
		
		# Check if the selected item was a sale item or auction item
		if sale_item:
			similar_items = getAllItemsFromCategory(sale_item[0]['category'], categories)
			# Randomize the items to be shown
			random.shuffle(similar_items)
			
			self.render("sale_item.html", item=sale_item[0], related_items=similar_items, user=self.session.get('user'))
		
		else:
			auction_item = getAuctionItem(item_id)
			similar_items = getAllItemsFromCategory(auction_item[0]['category'], categories)
			# Randomize the items to be shown
			random.shuffle(similar_items)
			
			self.render("auction_item.html", item=auction_item[0], related_items=similar_items, user=self.session.get('user'))



class LoginPage(Handler):
	def get(self):
		self.render("login.html", error_msg="")
	
	def post(self):
		username = cgi.escape(self.request.get('username'))
		password = cgi.escape(self.request.get('password'))
		
		current_user = login(username, password)
		
		if current_user is not None:
			self.session['user'] = current_user
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
		name = cgi.escape(self.request.get('fullname'))
		email = cgi.escape(self.request.get('email'))
		birthdate = cgi.escape(self.request.get('year')) + '-' + cgi.escape(self.request.get('month')) + '-' + cgi.escape(self.request.get('day'))
		username = cgi.escape(self.request.get('username'))
		password = cgi.escape(self.request.get('password'))
		street = cgi.escape(self.request.get('street'))
		city = cgi.escape(self.request.get('city'))
		state = cgi.escape(self.request.get('state'))
		zipcode = cgi.escape(self.request.get('zipcode'))
		phone = cgi.escape(self.request.get('phone'))
		card_num = cgi.escape(self.request.get('card_num'))
		card_type = cgi.escape(self.request.get('card_type'))
		income = cgi.escape(self.request.get('income'))
		gender = cgi.escape(self.request.get('gender'))
		
		if insertIntoUsers(name, email, float(income), gender, username, password, birthdate):
			message = "Hi " + name + "! Welcome to Moogle. Hope you have a lot of fun!\nYour username is " + username
			mail.send_mail(sender="mooglethestore@gmail.com",to=email,subject="Hi from Moogle!",body=message)
			self.redirect("/")
		else:
			self.render("signup.html",msg="USERNAME ALREADY IN USE")


# Action to be performed when a user enters a search query
class SearchStore(Handler):
	def post(self):
		query = cgi.escape(self.request.get('query'))
		category = cgi.escape(self.request.get('cat'))
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
	('/search', SearchStore),
	('/testpost', TestPagePost),
	], debug=True, config=config)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
