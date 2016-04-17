import os
import cgi
import jinja2
import webapp2
import MySQLdb
import urllib
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
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
    


############################################################################################################



# Home page
class MainPage(Handler):
	def get(self):
		categories = getAllCategories()
		items = getAllItems()
		
		self.render("category.html", currentCategory='All', items=items, categories=categories, user=self.session.get('user'))




class CategoryPage(Handler):
	def get(self):
		selectedCategory = self.request.get("cat")
		categories = getAllCategories()
		
		items = getAllItemsFromCategory(selectedCategory, categories)
		
		self.render("category.html", currentCategory=selectedCategory, items=items, categories=categories, user=self.session.get('user'))



		

class ItemPage(Handler):
	def get(self):
		item_id = str(self.request.get("id"))
		sale_item = getSaleItem(item_id)
		#similar_items = 
		
		# Check if the selected item was a sale item or auction item
		if sale_item:
			self.render("sale_item.html", item=sale_item[0], user=self.session.get('user'))
		else:
			auction_item = getAuctionItem(item_id)
			self.render("auction_item.html", item=auction_item[0], user=self.session.get('user'))



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
	('/testpost', TestPagePost),
	], debug=True, config=config)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
