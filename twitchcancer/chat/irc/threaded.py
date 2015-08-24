#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request
import time
import random
from threading import Thread

import logging
logger = logging.getLogger(__name__)

from twitchcancer.chat.monitor import Monitor
from twitchcancer.chat.irc.irc import IRC

from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.storage.storage import Storage

class ThreadedIRCMonitor(Monitor):

  def __init__(self, viewers):
    super().__init__(viewers)

    self.storage = Storage()
    self.diagnosis = Diagnosis()
    self.clients = {}

  # fake a channels property, extracted from clients
  def __getattr__(self, attr):
    if attr == "channels":
      return [channel for client in self.clients.values() for channel in client.channels]

  # run the main thread, it'll auto add channels and mainly sleep
  def run(self):
    try:
      while True:
        self.autojoin()

        logger.info("cycle ran with %s clients and %s channels over %s viewers up", len(self.clients), len(self.channels), self.viewers)

        # wait until our next cycle
        time.sleep(60)
    except KeyboardInterrupt:
      pass

  # connect to a server
  def connect(self, server):
    # don't connect to the same server twice
    if server in self.clients:
      return

    logger.debug("connecting to %s", server)

    (ip, port) = server.split(":")
    client = IRC(ip, port)

    self.clients[server] = client

    t = Thread(name="Thread-"+server, target=_monitor_one, kwargs={'source':client, 'diagnosis': self.diagnosis, 'storage':self.storage})
    t.daemon = True
    t.start()
    logger.info("started monitoring %s in thread %s", server, t.name)

  # join a channel
  def join(self, channel):
    # don't join the same channel twice
    if channel in self.channels:
      #logger.debug("not re-joining %s", channel)
      return

    # get a random server hosting this channel
    server = self.find_server(channel)

    # connect to new servers
    self.connect(server)

    # join the channel
    logger.debug("will join %s on %s", channel, server)
    self.clients[server].join(channel)

  # leave a channel
  def leave(self, channel):
    # don't leave a channel we didn't join
    if channel not in self.channels:
      #logger.debug("not leaving un-joined channel %s", channel)
      return

    # tell the client to leave the channel
    logger.debug("will leave channel %s", channel)
    client = self.get_client(channel)
    client.leave(channel)

  # find a server hosting a channel
  def find_server(self, channel):
    with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel.replace("#", ""))) as response:
      j = json.loads(response.read().decode())
      return random.choice(j['chat_servers'])

  # join big channels, leave offline ones
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
            self.leave(channel)

        # join channels over n viewers, leave channels under n viewers
        for stream in data['streams']:
          if stream['viewers'] > self.viewers:
            self.join('#'+stream['channel']['name'])
          else:
            self.leave('#'+stream['channel']['name'])
    except urllib.error.URLError:
      # ignore the error, we'll try again next cycle
      pass

  # returns the client connected to the server where a channel was joined
  def get_client(self, channel):
    for client in self.clients.values():
      if channel in client.channels:
        return client
    return None

# read all messages the source generates
def _monitor_one(source, diagnosis, storage):
  for channel, message in source:
    # compute points for the message
    points = diagnosis.points(message)

    #print(message[0:20], channel)

    # store cancer records
    storage.store(channel, points)
