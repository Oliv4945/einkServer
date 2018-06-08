# -*- coding: utf-8 -*-

from flask import Flask
from config import basedir
import os

# Application
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object('config')

# Log to file if the application is not in debug
if not app.debug:
    if not os.path.exists('misc/log'):
        os.makedirs('misc/log')
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
                os.path.join(basedir, '../misc/log/ioPush.log'),
                'a', 1 * 1024 * 1024, 5
                )
    file_handler.setFormatter(logging.Formatter(
                      '''%(asctime)s %(levelname)s:
                         %(message)s [in %(pathname)s:%(lineno)d]
                      '''))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('**** START ****')

from app import views
