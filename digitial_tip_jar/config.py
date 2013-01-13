SECRET_KEY = '1JZPwvT7HkNhTWxoACAdQYkYqwbwoWmLpSGgArMF'
ERROR_LOG_PATH = '/root/error.log'
STATIC_URL = '/static/'
QR_PATH = '/root/digital_tip_jar/digitial_tip_jar'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Facebook OAuth
DEBUG = True
FACEBOOK_APP_ID = '420876154648502'
FACEBOOK_APP_SECRET = '9e6ce868fa5e31ba956a248b392c9f96'

PORT = 80
DOMAIN = 'http://digitaltipjar.homemadebyrobots.org/'

MOST_RECENT_SIZE = 1
RECENT_TIPS_SIZE = 20
IMAGE_SIZE = (300,1080)
UPLOAD_FOLDER = '/root/digital_tip_jar/digitial_tip_jar/static/profile'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 #16MB



try:
    from dev_config import *
except:
    pass
