#!/usr/bin/env python
import sys
from pymongo import MongoClient
import util

connection = MongoClient('localhost', 27017)
db = connection.register4rms
users = db.users # get a collection

user = { 
'username': sys.argv[1],
'pass': util.set_password(sys.argv[2]),
}

users.insert(user)