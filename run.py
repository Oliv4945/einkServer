#!virtualenv/bin/python
# -*- coding: utf-8 -*-

from app import app
app.run(host='0.0.0.0', port=4999, debug=True)
