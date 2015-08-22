#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import json
import asyncio
import logging
import random
logger = logging.getLogger(__name__)

from twitchcancer.chat.monitor import Monitor
from twitchcancer.chat.websocket.twitchclientfactory import TwitchClientFactory

class AsyncWebSocketMonitor(Monitor):

  def __init__(self, viewers):
    super().__init__(viewers)

    self.loop = asyncio.get_event_loop()
    self.servers = {}

  # join and leave channels, forever
  def run(self):
    self.loop.run_until_complete(self.mainloop())

  @asyncio.coroutine
  def mainloop(self):
    # every 60 seconds
    while True:
      # list new channel
      # join new big ones
      # leave dead ones
      yield from self.autojoin()

      logger.info("cycle ran with %s servers and %s channels over %s viewers up", len(self.servers), len(self.channels()), self.viewers)

      yield from asyncio.sleep(60)

  # connect to a server
  @asyncio.coroutine
  def connect(self, server):
    # don't connect twice to the same server
    if server in self.servers:
      return

    logger.debug("connecting to %s", server)

    (ip, port) = server.split(":")
    factory = TwitchClientFactory(loop=self.loop)
    factory.loop = self.loop
    factory.server = server

    self.servers[server] = factory

    coro = self.loop.create_connection(factory, ip, port)
    yield from coro

  # join a channel
  @asyncio.coroutine
  def join(self, channel):
    # don't join the same channel twice
    if channel in self.channels():
      #logger.debug("not re-joining %s", channel)
      return

    # get a random server hosting this channel
    server = self.find_server(channel)

    # connect to new servers
    yield from self.connect(server)

    # join the channel
    logger.debug("will join %s on %s", channel, server)
    yield from self.servers[server].client.join(channel)

  # leave a channel
  def leave(self, channel):
    pass

  # find a server hosting a channel
  def find_server(self, channel):
    with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel)) as response:
      j = json.loads(response.read().decode())
      return random.choice(j['web_socket_servers'])

  # join big channels
  @asyncio.coroutine
  def autojoin(self):
    # get a list of channels from https://api.twitch.tv/kraken/streams/?limit=100
    # join any channel over n viewers
    # leave any channel under n viewers (including offline ones)
    try:
      # synchronous HTTP request, fine because we'd sleep otherwise
      with urllib.request.urlopen('https://api.twitch.tv/kraken/streams/?limit=100') as response:
        data = json.loads(response.read().decode())

        # TODO: stop monitoring dead streams
        for stream in data['streams']:
          if stream['viewers'] > self.viewers:
            yield from self.join(stream['channel']['name'])
    except urllib.error.URLError:
      # ignore the error, we'll try again next cycle
      pass

  def channels(self):
    return [channel for server in self.servers.values() for channel in server.channels]

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

  monitor = AsyncWebSocketMonitor()
  monitor.run()

  '''
  print(channel_message("FDFDF DF SFD PRIVMSG #forsenlol :DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp DARKEST DUNGEON PogChamp"))
  print(channel_message(":tmi.twitch.tv CAP * ACK :twitch.tv/tags twitch.tv/commands twitch.tv/membership"))
  print(channel_message("@color=#119EBB;display-name=Lotware;emotes=490:0-1;subscriber=1;turbo=1;user-type= :lotware!lotware@lotware.tmi.twitch.tv PRIVMSG #trumpsc ::P"))
  print(channel_message("@color=#119EBB;display-name=Lotware;emotes=490:0-1;subscriber=1;turbo=1;user-type= :lotware!lotware@lotware.tmi.twitch.tv PRIVMSG #trumpsc :http://test.com      test  test"))
  '''
