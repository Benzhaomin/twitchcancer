#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bottle import Bottle, route, request, response, run
app = Bottle()

from twitchcancer.storage import Storage
storage = Storage()

@app.hook('after_request')
def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# returns the full history of a channel (5 minutes interval)
# curl http://localhost:8080/history/forsenlol
@app.route(path="/history/<channel>", method="GET")
def history_(channel):
  result = storage.history('#'+channel)

  return {'history': result}

# returns cancer level of
@app.route(path="/live", method="GET")
#@app.route(path="/live/<channels>", method="GET")
def cancer():
  result = storage.cancer()

  return {'channels': result}

def history(args):
  run(app, host=args.host, port=int(args.port)) #, debug=(numeric_level==logging.DEBUG)
