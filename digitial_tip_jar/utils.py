import re
import json
import qrcode
import uuid
from config import QR_PATH

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

def qrcode_string(string):
  qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
  )
  qr.add_data(string)
  qr.make(fit=True)
  img = qr.make_image()
  qr_url = '/static/qr/'+str(uuid.uuid4())+'.jpg'
  qrpath = QR_PATH + qr_url
  img.save(qrpath)
  return qr_url
    	
def slugify(value, users):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    slug = _slugify_hyphenate_re.sub('-', value)
    count = 0

    for user in users:
        if slug in user.user_name:
            count = count + 1

    if count > 0:
        slug = slug + str(count)

    return slug


def is_username_unique(user_name, users):
    for user in users:
        if user_name.lower() == user.user_name.lower():
            return False
    return True


def resize_image(file, size):
    import os
    from PIL import Image

    outfile = os.path.splitext(file)[0] + "_profile.jpg"
    if file != outfile:
        try:
            im = Image.open(file)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(outfile, "JPEG")
            return outfile
        except IOError:
            return None

    return file




class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'): #handles both date and datetime objects
            return obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        else:
            return json.JSONEncoder.default(self, obj)
