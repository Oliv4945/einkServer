#-*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# General
WTF_CSRF_ENABLED = True
SECRET_KEY = 'A-long-enough-random-key'

# API Keys
API_KEY_HASS = 'Home assistant API key'
API_KEY_OWM = 'OpenWeatherMap API key'
