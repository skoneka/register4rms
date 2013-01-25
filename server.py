#!/usr/bin/env python
# register4rms
# webpage: https://github.com/skoneka/register4rms
# author: Artur Skonecki

import sys
import tornado
from tornado import web
from tornado import ioloop
import tornado.httpserver
import util

from pymongo import MongoClient

#import ipdb

connection = MongoClient('localhost', 27017)
db = connection.register4rms
attendees = db.attendees
users = db.users

class MainHandler(web.RequestHandler):
  def get(self):
    self.render('index.html')

class AdminHandler(web.RequestHandler):
  def get_current_user(self):
    return self.get_secure_cookie("user")

  @tornado.web.authenticated
  def get(self):
    a = db.attendees.find()
    self.render('admin.html', attendees = a)

class LogoutHandler(web.RequestHandler):
  def get(self):
    self.clear_cookie("user")
    self.redirect('/login')

class RegisterHandler(web.RequestHandler):
  def get(self):
    self.render('register.html')
    
  def post(self):
    try:
      attendee = { 
      'name': self.get_argument("name"),
      'surname': self.get_argument("surname"),
      'email':  self.get_argument("email"),
      }
      attendees.insert(attendee)
      self.redirect("/register")
    except:
      self.write('<br> Incomplete fields')


class LoginHandler(MainHandler):
  def get(self):
    self.render('login.html')

  def post(self):
    username = self.get_argument("username")
    password = self.get_argument("pass")
    users = db.users.find({'username': username})
    try:
      user = next(users)
    except StopIteration:
      self.redirect("/")
    #ipdb.set_trace()
    if user['username'] == username and util.check_password(password, user['pass']):
      self.set_secure_cookie("user", self.get_argument("username"))
    self.redirect("/admin")

def main():
  application = tornado.web.Application (
    [
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/admin", AdminHandler),
    (r"/register", RegisterHandler)
    ],
    debug=True,
    cookie_secret='testSAKDFJAWIEOJVNMMLREPOQRIUIUFAHJVLKGJHGLLADF',
    login_url= "/login"
  )
  http_server = tornado.httpserver.HTTPServer(application)

  http_server.listen(sys.argv[1])
  print('server@'+sys.argv[1])
  ioloop.IOLoop.instance().start ()
    
if __name__ == '__main__':
  main()
  