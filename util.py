import hashlib

def get_hexdigest(algo, salt, raw_password):
  return hashlib.sha1('%s%s' % (salt, raw_password)).hexdigest()

def set_password(raw_password):
  import random
  algo = 'sha1'
  salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
  hsh = get_hexdigest(algo, salt, raw_password)
  password = '%s$%s$%s' % (algo, salt, hsh)
  return password
  
def check_password(raw_password, enc_password):
  """
  Returns a boolean of whether the raw_password was correct. Handles
  encryption formats behind the scenes.
  """
  algo, salt, hsh = enc_password.split('$')
  return hsh == get_hexdigest(algo, salt, raw_password)