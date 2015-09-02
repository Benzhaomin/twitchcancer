#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import asyncio
import logging
logger = logging.getLogger(__name__)

from autobahn.asyncio.websocket import WebSocketClientProtocol

from twitchcancer.config import Config
from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.storage.storage import Storage

diagnosis = Diagnosis()
storage = Storage()

@asyncio.coroutine
def record(parsed):
  # compute points for the message
  points = diagnosis.points(parsed['message'])

  # store cancer records for later
  storage.store(parsed['channel'], points)
  #print(parsed['channel'], points)

class TwitchClient(WebSocketClientProtocol):

  def onOpen(self):
    self.sendMessage('CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership'.encode())
    self.sendMessage('PASS {0}'.format(Config.get("monitor.chat.password").lower()).encode())
    self.sendMessage('NICK {0}'.format(Config.get("monitor.chat.username").lower()).encode())

    for channel in self.channels:
      self.sendMessage('JOIN {0}'.format(channel).encode())
      logger.info("auto-joining %s", channel)

  def onMessage(self, payload, isBinary):
    if isBinary:
      logger.debug("Binary message received: {0} bytes".format(len(payload)))
    else:
      message = payload.decode('utf8')

      # respond to PING
      if message[0:4] == "PING":
        self.sendMessage('PONG :tmi.twitch.tv'.encode())
        logger.debug("PONG-ed")
      # try to parse and record messages
      else:
        parsed = TwitchClient.parse_message(message)
        if parsed:
          yield from record(parsed)

  @asyncio.coroutine
  def join(self, channel):
    self.channels.add(channel)
    self.sendMessage('JOIN {0}'.format(channel).encode())
    logger.info("joining %s", channel)

  @asyncio.coroutine
  def leave(self, channel):
    self.channels.remove(channel)
    self.sendMessage('PART {0}'.format(channel).encode())
    logger.info("leaving %s", channel)

  channel_message_re = re.compile(".*? PRIVMSG (#[a-zA-z0-9_]*?) :(.*)")

  @classmethod
  def parse_message(cls, line):
    match = cls.channel_message_re.match(line)

    if match:
      return {
        'channel': match.group(1),
        'message': match.group(2).replace('\x01ACTION ', '').replace('\x01', '')
      }

    return None

'''
if __name__ == "__main__":
  import yappi

  yappi.start()

  with open("../websocket.log") as f:
    for l in f:
      assert TwitchClient.parse_message(l) TwitchClient.RE_parse_message(l)


  yappi.get_func_stats().print_all()
  yappi.get_thread_stats().print_all()
'''
