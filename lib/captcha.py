#
#  Simple CAPTCHA Generator for Python (Web) Frameworks
# ======================================================
#  Copyright 2010 Paul Banks [http://paulbanks.org/contact]
#
#  This file is free software: you may copy, redistribute and/or modify it  
#  under the terms of the GNU General Public License as published by the  
#  Free Software Foundation, either version 2 of the License, or (at your  
#  option) any later version.  
#  
#  This file is distributed in the hope that it will be useful, but  
#  WITHOUT ANY WARRANTY; without even the implied warranty of  
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU  
#  General Public License for more details.  
#  
#  You should have received a copy of the GNU General Public License  
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import Crypto.Cipher.AES as aes 
import base64
import random

import Image, ImageFont, ImageDraw, StringIO

#TODO: CHANGE THIS KEY! 
# IT MUST BE 16 BYTES LONG!
# >>>>>>>>>>>|................|
captchakey = "SPAMMERSBESHOT!!";
#captchafont = "/usr/share/fonts/dejavu/DejaVuSans.ttf";
captchafont = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
#captchafont = '/usr/local/lib/X11/fonts/dejavu/DejaVuSans.ttf'

def GenerateID():

    # Generate random text for Captcha
    imgtext = ''.join([random.choice('1234567890') for i in range(5)])

    # Encrypt it
    iv = ''.join([chr(random.randint(0, 255)) for i in range(16)])
    a = aes.new(captchakey, mode=aes.MODE_CBC, IV=iv);
    padVal = aes.block_size - (len(imgtext) % aes.block_size);
    imgtext += chr(padVal) * padVal
    crypttext = a.encrypt(imgtext);

    # Return encoded ID safe for URLs
    return base64.b16encode(iv) + base64.b16encode(crypttext)

def Decrypt(id):
    iv = base64.b16decode(id[0:32])
    crypttext = base64.b16decode(id[32:])
    a = aes.new(captchakey, mode=aes.MODE_CBC, IV=iv);
    imgtext = a.decrypt(crypttext)
    return imgtext[:5]

def GenerateImage(id):

    # Decrypt captcha id 
    imgtxt = Decrypt(id)

    # Render captcha image
    font = ImageFont.truetype(captchafont, 24)
    sw, sh = font.getsize(imgtxt)            
    im = Image.new('RGB', (sw+6,sh+6), 0xffffaa)
    d = ImageDraw.Draw(im)
    x, y = im.size
    d.text((3,3), imgtxt, font=font, fill=0)
   
    # Return image data as a python string    
    buffer = StringIO.StringIO()
    im.save(buffer, "PNG")
    return buffer.getvalue()

def Check(usertext, captchaid):
    if (Decrypt(captchaid)==usertext):
        return 1
    return 0

