#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import logging
logger = logging.getLogger(__name__)

from twitchcancer.storage.storage import Storage

'''
  handles:
    'twitchcancer.search': search for a channel by name
'''
# handles one-time requests
class RequestHandler:

  __instance = None

  # poor man's singleton
  def instance():
    if RequestHandler.__instance is None:
      RequestHandler.__instance = RequestHandler()
    return RequestHandler.__instance

  def __init__(self):
    self.storage = Storage()

  # respond to a request
  def handle(self, request):
    try:
      # search_channel requests
      if request['request'] == "twitchcancer.search":
        # we need a channel to search for
        if request['data'] is not None:
          return self.storage.search(request['data'])
    except KeyError:
      logger.warning("got a malformed request %s", request)
    except TypeError:
      logger.warning("got a malformed request %s", request)

    return {}
