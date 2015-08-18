#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import datetime
import logging
import threading
logger = logging.getLogger(__name__)

'''
  Schema

  messages {
    date: datetime of creation
    channel: "#channel",
    cancer: cancer points,
  }
'''

# the in-memory store handles messages streaming in
class InMemoryStore:

  def __init__(self):
    super().__init__()

    # store messages in memory only
    self.messages = collections.deque()
    self.messages_lock = threading.Lock()

    logger.debug('created an InMemorytStore object')

  # returns a summary of cancer and message by channel grouped by minute, processed messages are deleted forever
  # @memory.read()
  def archive(self):
    # debugging
    now_start = datetime.datetime.now(datetime.timezone.utc)
    message_delta = 0
    logger.debug('archive started at %s with %s messages total', now_start, len(self.messages))

    # run at 12:31:20
    # bp  at 12:30:00
    breakpoint = self._live_message_breakpoint()
    breakpoint = breakpoint.replace(second=0, microsecond=0)

    '''
      map/reduce self.messages into history = {
        '{minute}': {
          '{channel} {
            'cancer: cancer points,
            'messages': messages count
          }
      }
    '''
    history = collections.defaultdict(lambda: collections.defaultdict(lambda: {'cancer': 0, 'messages': 0}))

    # run until there's no old message left
    with self.messages_lock:
      while True:
        try:
          message = self.messages.popleft()
        except IndexError:
          logger.info('archive ate all the messages, meaning we got no message in the last minute')
          break

        # group messages by minute
        message['date'] = message['date'].replace(second=0, microsecond=0)

        # stop if the message is too new
        if message['date'] >= breakpoint:
          self.messages.appendleft(message)
          logger.debug('archiving loop stopped at message %s', message['date'])
          break

        # defaultdict builds everything as needed
        history[message['date']][message['channel']]['cancer'] += message['cancer']
        history[message['date']][message['channel']]['messages'] += 1

        # debugging
        message_delta += 1

    # debugging
    now_end = datetime.datetime.now(datetime.timezone.utc)
    logger.debug('archived %s messages in %s ms, %s messages left', message_delta, (now_end - now_start).total_seconds() * 1000, len(self.messages))

    return history

  # returns live cancer levels based on self.messages
  # @memory.read()
  def cancer(self):
    breakpoint = self._live_message_breakpoint()
    minute = collections.defaultdict(lambda: {'cancer': 0, 'messages': 0})

    # sum cancer points and count recent messages for each channel
    with self.messages_lock:
      for message in reversed(self.messages):
        if message['date'] < breakpoint:
          break

        minute[message['channel']]['cancer'] += message['cancer']
        minute[message['channel']]['messages'] += 1

    return [{
      'channel': channel,
      'cancer': records['cancer'],
      'messages': records['messages'],
    } for channel, records in minute.items()]

  # store a cancer level for a single message in a channel
  # @memory.write()
  def store(self, channel, cancer):
    message = {
      'date': datetime.datetime.now(datetime.timezone.utc),
      'channel': channel,
      'cancer': int(cancer)
    }

    with self.messages_lock:
      self.messages.append(message)

  # returns the datetime where live and archived messages split
  def _live_message_breakpoint(self):
    # messages are old and ready to be archived after 1 minute
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1))
