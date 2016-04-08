import os
import cgi
import jinja2
import webapp2
import MySQLdb
import urllib
from google.appengine.ext.webapp.util import run_wsgi_app
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



# ID of the current user (-1 if user not logged in)
current_user=-1

# Home page
class MainPage(Handler):
	def get(self):
		categories = getAllCategories()
		items = getAllItems()
		
		self.render("category.html", currentCategory='All', items=items, categories=categories)




class CategoryPage(Handler):
	def get(self):
		selectedCategory = self.request.get("cat")
		categories = getAllCategories()
		
		items = getAllItemsFromCategory(selectedCategory, categories)
		
		
		self.render("category.html", currentCategory=selectedCategory, items=items, categories=categories)



		
class TestPageGet(Handler):
	def write_form(self, items=None):
		self.render("testing.html",items=items)

	def get(self):
		
		items = getAllItems()		
		
		self.write_form(items)





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
		






application = webapp2.WSGIApplication([
	('/', MainPage),
	(r'/category.*', CategoryPage),
	('/testget', TestPageGet),
	('/testpost', TestPagePost),
	], debug=True)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
