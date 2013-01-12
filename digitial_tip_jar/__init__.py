from flask import Flask
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config.from_object('hungry_now.config')

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(app.config['ERROR_LOG_PATH'], maxBytes=1000000 )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)

import hungry_now.views
