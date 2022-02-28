    
import urllib.request
import datetime
from PIL import Image, ImageOps
import os

def generate_filename():
    base = "image"
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = "_".join([base, suffix])
    return filename


def img_dl(img_url):
    
    #filename = generate_filename()
    resp = urllib.request.urlopen(img_url)
    

    if resp.code == 200:
        img = urllib.request.urlopen(img_url).read()
        img_data = open('static/default.jpg', 'wb')
        img_data.write(img)
        img_data.close()
    

img_dl("https://www.unsw.edu.au/etc/clientlibs/unsw-common/unsw-assets/img/social/UNSWlogo-opengraph-squaresafe.png")
size = (225, 225)
profile = Image.open("static/default.jpg")
profile = ImageOps.fit(profile, size, Image.ANTIALIAS)
profile.save("static/unswstreams.jpg")
