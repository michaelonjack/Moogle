# CMPSC_431W_Project

HOMEPAGE
http://moogle-store.appspot.com

TEST YOUR HTML/CSS
https://jsfiddle.net

JINJA2 DOC
http://jinja.pocoo.org/docs/dev/


Once you get Ubuntu running on a virtual machine, follow these steps to run moogle on your local host:
0.) Pull the github project to your virtual machine
1.) Find the ip address of your virtual machine. You can do this by simply googling "my ip address"
2.) Send me this ip address on groupme or whatever
3.) Once I authorize your ip address enter the follow command at the terminal:

>path/to/google_appengine/dev_appserver.py path/to/moogle

where path/to/goole_appengine is the path to the google_appengine directory which is on github inside the main directory
and path/to/moogle is the path to the moogle directory which is also on github inside the main directory

4.) If all goes well, this command should launch the application server which will continue to run until you press Ctrl-C. You will probably be asked for a google email and password at this step, the email address is "mooglethestore@gmail.com" and then ask me for the password.

You can now view the application on your local host which you can access at http://localhost:8080

5.) To view and edit your HTML file on the application server, upload the html file that you will be using (can be blank for now) to github and let me know. I'll send back the URL you can use to view this file in the application server. For example, if you tell me you uploaded and will be editing the file 'mypage.html', I'll tell you can view it at '/yourpage' which means you can view the file at http://localhost:8080/yourpage while the app server is running

