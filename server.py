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

import lib.captcha as captcha

#import ipdb

connection = MongoClient('localhost', 27017)
db = connection.register4rms
attendees = db.attendees
users = db.users

class CaptchaException(Exception):
  pass


class MainHandler(web.RequestHandler):
  def get(self):
    captchaId = captcha.GenerateID()
    captcha_html = '''
      <img src="%s" />
      What is the number: <input type="text" name="fUserField" />
      <input type="hidden" name="fCaptchaH" value="%s" />
      ''' % ("/a/captcha/?id="+captchaId, captchaId)
    cImg = captcha.GenerateImage(captchaId)
    last_img = cImg
    self.render('index.html', captcha = captcha_html)

  def post(self):
    try:
      attendee = {
      'name': self.get_argument("name"),
      'surname': self.get_argument("surname"),
      'email':  self.get_argument("email"),
      }
      try:
        fUserField = self.get_argument("fUserField")
        if captcha.Check( self.get_argument("fUserField"), self.get_argument("fCaptchaH") ):
          attendees.insert(attendee)
          self.redirect("/register")
        else:
          raise CaptchaException
      except:
        self.write('<br> Incorrect captcha')
    except:
      self.write('<br> Incomplete fields')


class CaptchaImageDispatcher(tornado.web.RequestHandler):
    def get(self):
      captchaId = self.get_argument('id')
      self.add_header("Content-Type", "image/png")
      self.write(captcha.GenerateImage(captchaId))


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


class LoginHandler(MainHandler):
  def get(self):
    self.render('login.html')

  def post(self):
    try:
      username = self.get_argument("username")
      password = self.get_argument("pass")
    except:
      self.write('<br> Incomplete fields')
    try:
      users = db.users.find({'username': username})
      user = next(users)
      if user['username'] == username and util.check_password(password, user['pass']):
        self.set_secure_cookie("user", self.get_argument("username"))
        self.redirect("/admin")
    except StopIteration:
      self.redirect("/login")


def main():
  application = tornado.web.Application (
    [
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/a/captcha/.*", CaptchaImageDispatcher),
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
  
