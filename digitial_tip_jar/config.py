SECRET_KEY = '1JZPwvT7HkNhTWxoACAdQYkYqwbwoWmLpSGgArMF'
ERROR_LOG_PATH = '/root/error.log'
STATIC_URL = '/static/'
QR_PATH = '/root/digital_tip_jar/digitial_tip_jar'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# Facebook OAuth
DEBUG = True
FACEBOOK_APP_ID = '420876154648502'
FACEBOOK_APP_SECRET = '9e6ce868fa5e31ba956a248b392c9f96'

PORT = 80
DOMAIN = 'http://digitaltipjar.homemadebyrobots.org/'



try:
    from dev_config import *
except:
    pass
