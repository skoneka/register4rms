#!/usr/bin/env python
# register4rms
# webpage: https://github.com/skoneka/register4rms
# author: Artur Skonecki
# author: Barnaba Turek

import sys
import tornado
from tornado import web
from tornado import ioloop
from tornado import escape
import tornado.httpserver
from tornado.web import HTTPError
import util
import os

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
    captcha_img_html = '''
      <img class="controls" src="%s" />
    '''% ("/a/captcha/?id="+captchaId)
    captcha_form_html = '''
      <input type="text" name="fUserField" class="controls" />
      <input type="hidden" name="fCaptchaH" value="%s" />
      ''' % ( captchaId)
    cImg = captcha.GenerateImage(captchaId)
    last_img = cImg
    success = self.get_argument("success", None, True)
    msg = escape.url_unescape(self.get_argument("msg", "", True))
    self.render('index.html', captcha_img = captcha_img_html, captcha_form = captcha_form_html, success = success, msg = msg)

  def post(self):
    success=False
    
    try:
      self.get_argument("kotiknews-events")
      bKotikNews = True
    except HTTPError:
      bKotikNews = False
      
    try:
      attendee = {
      'name': self.get_argument("name"),
      'surname': self.get_argument("surname"),
      'email':  self.get_argument("email"),
      'kotiknews-events': bKotikNews,
      }
      print(attendee)
      try:
        fUserField = self.get_argument("fUserField")
        if captcha.Check( self.get_argument("fUserField"), self.get_argument("fCaptchaH") ):
          attendees.insert(attendee)
          success=True
          msg="Registration complete. Thank you."
        else:
          raise CaptchaException
      except:
        msg = "Incorrect captcha"
    except:
      msg = "Please fill in all fields"
    path = "/?success=%s&msg=%s" % (success, escape.url_escape(msg))
    self.redirect(path, permanent=False)


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
    login_url= "/login",
    static_path = os.path.join(os.path.dirname(__file__), "static")
  )
  http_server = tornado.httpserver.HTTPServer(application)

  http_server.listen(sys.argv[1])
  print('server@'+sys.argv[1])
  ioloop.IOLoop.instance().start ()
    
if __name__ == '__main__':
  main()
  
