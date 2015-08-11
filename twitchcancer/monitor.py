#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from queue import Queue
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.diagnosis import Diagnosis
from twitchcancer.storage import Storage

# worker thread
def _monitor_one(source, queue):
  diagnosis = Diagnosis()

  for message in source:
    queue.put((source.name(), diagnosis.cancer(message)))

# main thread
def monitor(sources):
  queue = Queue()

  for source in sources:
    t = Thread(name="Thread "+source.name(), target=_monitor_one, kwargs={'source':source, 'queue':queue})
    t.daemon = True
    t.start()

  storage = Storage()

  try:
    while True:
      (channel, cancer) = queue.get()

      storage.store(channel, cancer)
  except KeyboardInterrupt:
    # flush db to disk
    pass
