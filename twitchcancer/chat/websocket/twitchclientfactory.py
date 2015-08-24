#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import json
import asyncio
import logging
import random
logger = logging.getLogger(__name__)

from autobahn.asyncio.websocket import WebSocketClientFactory

from twitchcancer.chat.websocket.twitchclient import TwitchClient

class TwitchClientFactory(WebSocketClientFactory):

  protocol = TwitchClient

  def __init__(self, *args, **kwargs):
    self.client = None
    WebSocketClientFactory.__init__(self, *args, **kwargs)

  def __call__(self):
    proto = self.protocol()
    proto.factory = self
    proto.channels = set()

    self.client = proto
    logger.debug('created a client for server %s', self.server)
    return proto

  @asyncio.coroutine
  def join(self, channel):
    yield from self.client.join(channel)

  @asyncio.coroutine
  def leave(self, channel):
    yield from self.client.leave(channel)

  def __getattr__(self, attr):
    if attr == "channels":
      return self.client.channels
