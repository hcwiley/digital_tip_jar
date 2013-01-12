SECRET_KEY = '1JZPwvT7HkNhTWxoACAdQYkYqwbwoWmLpSGgArMF'
ERROR_LOG_PATH = '/root/error.log'
STATIC_URL = '/static/'
QR_PATH = '/root/digital_tip_jar/digitial_tip_jar'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

try:
    from dev_config import *
except:
    pass
