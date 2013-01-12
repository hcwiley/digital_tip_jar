SECRET_KEY = ''
ERROR_LOG_PATH = ''
STATIC_URL = '/static/'

try:
    from dev_config import *
except:
    pass
