#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from threading import Thread

import logging
logger = logging.getLogger(__name__)

from twitchcancer.chat.monitor import Monitor
from twitchcancer.chat.irc.irc import IRC

from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.storage.storage import Storage
from twitchcancer.utils.twitchapi import TwitchApi

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

    logger.info("connecting to %s", server)

    (ip, port) = server.split(":")
    client = IRC(ip, port)

    self.clients[server] = client

    t = Thread(name="Thread-"+server, target=_monitor_one, kwargs={'source':client, 'diagnosis': self.diagnosis, 'storage':self.storage})
    t.daemon = True
    t.start()
    logger.debug("started monitoring %s in thread %s", server, t.name)

  # join a channel
  def join(self, channel):
    # don't join the same channel twice
    if channel in self.channels:
      #logger.debug("not re-joining %s", channel)
      return

    # get a random server hosting this channel
    server = self.find_server(channel)

    # if we didn't get a server for whatever reason just exit here and stay open to retries
    if not server:
      return

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
    client = self.get_client(channel)

    if client:
      logger.debug("will leave channel %s", channel)
      client.leave(channel)
    else:
      logger.warning("couldn't find the client connected to %s", channel)

  # find a server hosting a channel
  def find_server(self, channel):
    try:
      result = TwitchApi.chat_properties(channel)

      if result:
        return random.choice(result['chat_servers'])
    except KeyError as e:
      logger.warning("got an empty json response to a chat properties request %s", e)

    return None

  # join big channels, leave offline ones
  def autojoin(self):
    # get a list of channels from Twitch
    # join any channel over n viewers
    # leave any channel under n viewers (including offline ones)
    try:
      data = TwitchApi.stream_list()

      if not data:
        return

      # extract a list of channels from Twitch's API response
      online_channels = ['#'+stream['channel']['name'] for stream in data['streams']]

      # ignore Twitch's data if it looks buggy (no streams online is unlikely)
      if (len(online_channels) == 0):
        return

      # leave any channel out of the top 100 (offline or just further down the list)
      for channel in self.channels:
        if channel not in online_channels:
          self.leave(channel)

      # join channels over n viewers, leave channels under n viewers
      for stream in data['streams']:
        if stream['viewers'] > self.viewers:
          self.join('#'+stream['channel']['name'])
        else:
          self.leave('#'+stream['channel']['name'])
    except KeyError as e:
      logger.warning("got an empty json response to a stream list request %s", e)
      return

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
