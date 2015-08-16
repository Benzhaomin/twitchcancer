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

from twitchcancer.diagnosis import Diagnosis
from twitchcancer.storage import Storage
from twitchcancer.source.twitch import Twitch

# profiling: import yappi

class Sleeper():

  def __init__(self):
    self.storage = Storage(cron=True)
    self.queue = Queue()
    self.sources = []

  def run(self, auto=True):
    try:
      while True:
        # auto monitor big streams
        if auto:
          # synchronous HTTP request, fine because we'd sleep otherwise
          with urllib.request.urlopen('https://api.twitch.tv/kraken/streams/?limit=100') as response:
            data = json.loads(response.read().decode())

            # TODO: stop monitoring dead streams
            for stream in data['streams']:
              # TODO: add this number as an option
              if stream['viewers'] > 3000:
                source = Twitch(stream['channel']['name'])
                self.monitor(source)

        logger.info("cycle ran with %s sources up", len(self.sources))

        # wait until our next cycle
        time.sleep(60)
    except KeyboardInterrupt:
      # flush db to disk
      pass

  def record(self):
    t = Thread(target=_record_cancer, kwargs={'queue':self.queue, 'storage':self.storage})
    t.daemon = True
    t.start()
    logger.info("started record cancer thread")

  # starts a monitor thread for the given source if it's not already running
  def monitor(self, source):
    if source in self.sources:
      return
    self.sources.append(source)

    t = Thread(name="Thread-"+source.name(), target=_monitor_one, kwargs={'source':source, 'queue':self.queue})
    t.daemon = True
    t.start()
    logger.info("started monitoring %s in thread %s", source.name(), t.name)

# record cancer thread, 1 per Sleeper
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

# monitor source thread, 1 per source
def _monitor_one(source, queue):
  # pass every message to the record queue
  for message in source:
    queue.put((source.name(), message))

def monitor(sources):
  # profiling: yappi.start()

  sleeper = Sleeper()

  # start the record thread
  sleeper.record()

  # start a monitoring thread for each source, if any
  for source in sources:
    sleeper.monitor(source)

  # run the main thread, it'll auto add sources if we don't have any
  sleeper.run(auto=(len(sources) == 0))

  # profiling: yappi.get_func_stats().print_all()
  # profiling: yappi.get_thread_stats().print_all()
