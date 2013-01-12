import re
import json
import qrcode

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

def qrcode(string):
  qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
  )
  qr.add_data(string)
  qr.make(fit=True)
  img = qr.make_image()
  qrpath = 'static/qr'+uuid.uuid4()+'.jpg'
  img.save(qrpath)
  return qrpath
    	
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




class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'): #handles both date and datetime objects
            return obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        else:
            return json.JSONEncoder.default(self, obj)
