#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
logger = logging.getLogger(__name__)

from autobahn.asyncio.websocket import WebSocketClientProtocol

from twitchcancer.chat.config import config as CONFIG
from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.storage.storage import Storage

diagnosis = Diagnosis()
storage = Storage()

@asyncio.coroutine
def record(parsed):
  if not parsed:
    return

  # compute points for the message
  points = diagnosis.points(parsed['message'])

  # store cancer records for later
  storage.store(parsed['channel'], points)
  #print(parsed['channel'], points)

def channel_message(line):
  cut = line.split("PRIVMSG")

  if len(cut) > 1:
    msg = cut[1].split(" :")

    if len(msg) > 1:
      channel = msg[0].strip()
      message = ' :'.join(msg[1:]).rstrip()

      if len(message) > 0:

        # strip /me from messages
        message = message.replace('\x01ACTION', '').replace('\x01', '')

        #print(message[0:20], channel)

        return {
          'channel': channel,
          'message': message
        }

  return None

class TwitchClient(WebSocketClientProtocol):

  def onOpen(self):
    self.sendMessage('CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership'.encode());
    self.sendMessage('PASS {0}'.format(CONFIG['password'].lower()).encode());
    self.sendMessage('NICK {0}'.format(CONFIG['username'].lower()).encode());

    for channel in self.channels:
      self.sendMessage('JOIN {0}'.format(channel).encode());
      logger.info("client auto-joining %s", channel)

  def onMessage(self, payload, isBinary):
    if isBinary:
      logger.debug("Binary message received: {0} bytes".format(len(payload)))
    else:
      message = payload.decode('utf8')

      # respond to PING
      if message[0:4] == "PING":
        self.sendMessage('PONG :tmi.twitch.tv'.encode());
        logger.debug("PONG-ed")
      # try to parse and record messages
      else:
        parse = channel_message(message)
        yield from record(parse)

  @asyncio.coroutine
  def join(self, channel):
    self.channels.add(channel)
    self.sendMessage('JOIN {0}'.format(channel).encode());
    logger.info("client joining %s", channel)

  @asyncio.coroutine
  def leave(self, channel):
    self.channels.remove(channel)
    self.sendMessage('PART {0}'.format(channel).encode());

if __name__ == "__main__":
  # profiling: import yappi

  # profiling: yappi.start()

  with open("../websocket.log") as f:
    for l in f:
      m = channel_message(l)
      if m:
        print(m)

  # profiling: yappi.get_func_stats().print_all()
  # profiling: yappi.get_thread_stats().print_all()
