#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
logger = logging.getLogger(__name__)

from autobahn.asyncio.websocket import WebSocketServerFactory

from twitchcancer.config import Config
from twitchcancer.api.pubsubprotocol import PubSubProtocol
from twitchcancer.api.pubsubtopic import PubSubTopic, PubSubVariableTopic
from twitchcancer.api.pubsubmanager import PubSubManager
from twitchcancer.storage.storage import Storage

# regularly publish data for a topic
@asyncio.coroutine
def publish(topic):
  while True:
    PubSubManager.instance().publish(topic)
    yield from asyncio.sleep(topic.sleep)

# build publishers coroutines
@asyncio.coroutine
def create_publishers():
  # setup storage
  storage = Storage()

  # list of topics clients can subscribe to
  topics = [
    PubSubTopic('twitchcancer.live', storage.cancer, 1),
    PubSubTopic('twitchcancer.leaderboards', storage.leaderboards, 60),
    PubSubVariableTopic('twitchcancer.leaderboard.*', storage.leaderboard, 60),
    PubSubTopic('twitchcancer.status', storage.status, 60),
    PubSubVariableTopic('twitchcancer.channel.*', storage.channel, 60),
  ]

  # add publisher tasks to the loop
  tasks = [publish(topic) for topic in topics]
  logger.info('added publisher topics: %s', ', '.join(map(str, topics)))

  yield from asyncio.gather(*tasks)

# run the websocket server
def run(args):
  factory = WebSocketServerFactory()
  factory.protocol = PubSubProtocol

  # setup the main event loop for network i/o
  loop = asyncio.get_event_loop()
  coro = loop.create_server(factory, Config.get('expose.websocket.host'), Config.get('expose.websocket.port'))
  server = loop.run_until_complete(coro)

  # setup publishers coroutines
  publishers = create_publishers()
  loop.run_until_complete(publishers)

  try:
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    publishers.close()
    server.close()
    loop.close()
