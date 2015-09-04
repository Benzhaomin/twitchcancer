#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from twitchcancer.storage.storageinterface import StorageInterface

'''
  Encapsulates three use-cases:

  # handle the message stream (memory-only):
    goal: store messages in memory and publish summaries
    user: monitoring process
    reqs: zmq
    uses: @memory.read()
          @memory.write()
          @socket.read()
          @socket.write()

  # keep track of leaderboards (write-only):
    goal: listen for summaries to update persistent leaderboards
    user: recording process
    reqs: zmq, pymongo
    uses: @socket.read()
          @db.write()

  # expose the entire model (read-only):
    goal: read data, some comes from the persistent store, some comes from the in-memory store
    user: api and anybody else
    reqs: zmq, pymongo
    uses: @socket.read()
          @db.read()

  Which concrete storage is needed is decided at runtime when any method is called
'''
class Storage(StorageInterface):

  def __init__(self):
    super().__init__()

    self.storage = None

  # defaults to ReadOnlyStorage
  def cancer(self):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.cancer()

  # defaults to ReadOnlyStorage
  def leaderboards(self):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.leaderboards()

  # defaults to ReadOnlyStorage
  def leaderboard(self, name):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.leaderboard(name)

  # defaults to ReadOnlyStorage
  def channel(self, channel):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.channel(channel)

  # defaults to ReadOnlyStorage
  def status(self):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.status()

  # defaults to MemoryStorage
  def store(self, channel, cancer):
    # messages are stored in-memory only
    if not self.storage:
      from twitchcancer.storage.memorystorage import MemoryStorage
      self.storage = MemoryStorage()

    self.storage.store(channel, cancer)

  # defaults to WriteOnlyStorage
  def record(self):
    # summaries are written to the database
    if not self.storage:
      from twitchcancer.storage.writeonlystorage import WriteOnlyStorage
      self.storage = WriteOnlyStorage()

    self.storage.record()

  # defaults to ReadOnlyStorage
  def search(self, channel):
    if not self.storage:
      from twitchcancer.storage.readonlystorage import ReadOnlyStorage
      self.storage = ReadOnlyStorage()

    return self.storage.search(channel)
