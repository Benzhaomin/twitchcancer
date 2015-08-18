#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import time
from threading import Thread
from queue import Queue
queue = Queue()

import logging
logger = logging.getLogger(__name__)

from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.storage.storage import Storage
from twitchcancer.monitor.twitch import Twitch

# profiling: import yappi

class ResidentSleeper():

  def __init__(self):
    self.storage = Storage()
    self.queue = Queue()
    self.sources = []

  # run the main thread, it'll auto add channels and mainly sleep
  def run(self, auto=True):
    try:
      while True:
        try:
          # synchronous HTTP request, fine because we'd sleep otherwise
          with urllib.request.urlopen('https://api.twitch.tv/kraken/streams/?limit=100') as response:
            data = json.loads(response.read().decode())

            # TODO: stop monitoring dead streams
            for stream in data['streams']:
              # TODO: add this number as an option
              if stream['viewers'] > 1000:
                source = Twitch(stream['channel']['name'])
                self.monitor(source)
        except urllib.error.URLError:
          # ignore the error, we'll try again next cycle
          pass

        logger.info("cycle ran with %s sources up", len(self.sources))

        # wait until our next cycle
        time.sleep(60)
    except KeyboardInterrupt:
      # flush db to disk
      pass

  # starts a record cancer thread, used for storage I/O
  def record(self):
    t = Thread(target=_record_cancer, kwargs={'queue':self.queue, 'storage':self.storage})
    t.daemon = True
    t.start()
    logger.info("started record cancer thread")

  # starts a monitor thread, used for network I/O
  # TODO: turn self.sources into a dict with channel name as key and source + thread objects as values
  def monitor(self, source):
    if source in self.sources:
      return
    self.sources.append(source)

    t = Thread(name="Thread-"+source.name(), target=_monitor_one, kwargs={'source':source, 'queue':self.queue})
    t.daemon = True
    t.start()
    logger.info("started monitoring %s in thread %s", source.name(), t.name)

# compute and store cancer for each message, 1 thread per instance
def _record_cancer(queue, storage):
  diagnosis = Diagnosis()

  while True:
    # get cancer records for channels
    (channel, message) = queue.get()

    # compute points for the message
    points = diagnosis.points(message)

    # store cancer records for later
    storage.store(channel, points)
    #logger.debug("Recorded cancer for channel %s", channel)

# eat what the source generates and put it into the record queue, 1 thread per source
def _monitor_one(source, queue):
  # pass every message to the record queue
  for message in source:
    queue.put((source.name(), message))

def run(args):
  # profiling: yappi.start()

  sleeper = ResidentSleeper()

  # start the record cancer thread
  sleeper.record()

  # run the main thread
  sleeper.run()

  # profiling: yappi.get_func_stats().print_all()
  # profiling: yappi.get_thread_stats().print_all()
