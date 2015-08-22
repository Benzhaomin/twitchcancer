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
    self.channels = set()
    self.servers = {}

  # run the main thread, it'll auto add channels and mainly sleep
  def run(self):
    try:
      while True:
        self.autojoin()

        logger.info("cycle ran with %s servers and %s channels over %s viewers up", len(self.servers), len(self.channels), self.viewers)

        # wait until our next cycle
        time.sleep(60)
    except KeyboardInterrupt:
      pass

  # connect to a server
  def connect(self, server):
    # don't connect to the same server twice
    if server in self.servers:
      return

    logger.debug("connecting to %s", server)

    (ip, port) = server.split(":")
    client = IRC(ip, port)

    self.servers[server] = client

    t = Thread(name="Thread-"+server, target=_monitor_one, kwargs={'source':client, 'diagnosis': self.diagnosis, 'storage':self.storage})
    t.daemon = True
    t.start()
    logger.info("started monitoring %s in thread %s", server, t.name)

  # store the client object connected to a server
  def connected(self, server, client):
    pass

  # join a channel
  def join(self, channel):
    # don't join the same channel twice
    if channel in self.channels:
      #logger.debug("not re-joining %s", channel)
      return

    self.channels.add(channel)

    # get a random server hosting this channel
    server = self.find_server(channel)

    # connect to new servers
    self.connect(server)

    # join the channel
    logger.debug("will join %s on %s", channel, server)
    self.servers[server].join(channel)

  # leave a channel
  def leave(self, channel):
    pass

  # find a server hosting a channel
  def find_server(self, channel):
    with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel)) as response:
      j = json.loads(response.read().decode())
      return random.choice(j['chat_servers'])

  # join big channels
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
          # TODO: add this number as an option
          if stream['viewers'] > self.viewers:
            self.join(stream['channel']['name'])
    except urllib.error.URLError:
      # ignore the error, we'll try again next cycle
      pass

# read all messages the source generates
def _monitor_one(source, diagnosis, storage):
  for channel, message in source:
    # compute points for the message
    points = diagnosis.points(message)

    #print(message[0:20], channel)

    # store cancer records
    storage.store(channel, points)
