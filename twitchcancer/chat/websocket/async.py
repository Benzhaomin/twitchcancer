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
    self.clients = {}

  # fake a channels property, extracted from clients
  def __getattr__(self, attr):
    if attr == "channels":
      return [channel for client in self.clients.values() for channel in client.channels]

  # join and leave channels, forever
  def run(self):
    self.loop.run_until_complete(self.mainloop())

  @asyncio.coroutine
  def mainloop(self):
    # every 60 seconds
    while True:
      yield from self.autojoin()

      logger.info("cycle ran with %s clients and %s channels over %s viewers up", len(self.clients), len(self.channels), self.viewers)

      yield from asyncio.sleep(60)

  # connect to a client
  @asyncio.coroutine
  def connect(self, server):
    # don't connect twice to the same server
    if server in self.clients:
      return

    logger.info("connecting to %s", server)

    (ip, port) = server.split(":")
    factory = TwitchClientFactory(loop=self.loop)
    factory.loop = self.loop
    factory.server = server

    self.clients[server] = factory

    coro = self.loop.create_connection(factory, ip, port)
    yield from coro

  # join a channel
  @asyncio.coroutine
  def join(self, channel):
    # don't join the same channel twice
    if channel in self.channels:
      #logger.debug("not re-joining %s", channel)
      return

    # get a random client hosting this channel
    server = self.find_server(channel)

    # connect to new clients
    yield from self.connect(server)

    # join the channel
    logger.debug("will join %s on %s", channel, server)
    yield from self.clients[server].join(channel)

  # leave a channel
  @asyncio.coroutine
  def leave(self, channel):
    # don't leave a channel we didn't join
    if channel not in self.channels:
      #logger.debug("not leaving un-joined channel %s", channel)
      return

    # tell the client to leave the channel
    logger.debug("will leave channel %s", channel)
    client = self.get_client(channel)
    yield from client.leave(channel)

  # find a server hosting a channel
  def find_server(self, channel):
    with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel.replace("#", ""))) as response:
      j = json.loads(response.read().decode())
      return random.choice(j['web_socket_servers'])

  # join big channels, leave offline ones
  @asyncio.coroutine
  def autojoin(self):
    # get a list of channels from https://api.twitch.tv/kraken/streams/?limit=100
    # join any channel over n viewers
    # leave any channel under n viewers (including offline ones)
    try:
      # synchronous HTTP request, fine because we'd sleep otherwise
      with urllib.request.urlopen('https://api.twitch.tv/kraken/streams/?limit=100') as response:
        data = json.loads(response.read().decode())

        # leave any channel out of the top 100 (offline or just further down the list)
        online_channels = ['#'+stream['channel']['name'] for stream in data['streams']]

        for channel in self.channels:
          if channel not in online_channels:
            yield from self.leave(channel)

        # join channels over n viewers, leave channels under n viewers
        for stream in data['streams']:
          if stream['viewers'] > self.viewers:
            yield from self.join('#'+stream['channel']['name'])
          else:
            yield from self.leave('#'+stream['channel']['name'])
    except urllib.error.URLError as e:
      # ignore the error, we'll try again next cycle
      logger.warn("stream list request failed %s", e)

  # returns the client connected to the server where a channel was joined
  def get_client(self, channel):
    for client in self.clients.values():
      if channel in client.channels:
        return client
    return None

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
