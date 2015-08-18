#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import logging
logger = logging.getLogger(__name__)

# ZeroMQ
import zmq

from twitchcancer.storage.persistentstore import PersistentStore
from twitchcancer.storage.storageinterface import StorageInterface
from twitchcancer.storage.storage import Storage

#
# keep leaderboards up-to-date with new data from the monitoring process
#
# implements:
#  - storage.record()
class WriteOnlyStorage(StorageInterface):

  def __init__(self):
    super().__init__()

    self._store = PersistentStore()

    # subscribe to summaries from the publisher socket
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.setsockopt(zmq.SUBSCRIBE, b'summary')
    self.socket.connect(Storage.SUMMARY_SOCKET_URI)
    logger.info("connected summary socket to %s", Storage.SUMMARY_SOCKET_URI)

  # start listening for summaries to persist
  # @socket.recv()
  # @db.write()
  def record(self):
    # update leaderboards with summaries we receive (one per channel per minute)
    while True:
      [topic,msg] = self.socket.recv_multipart()
      summary = pickle.loads(msg)
      self._store.update_leaderboard(summary)

# TODO: add proper unit testing
if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  storage = WriteOnlyStorage()

