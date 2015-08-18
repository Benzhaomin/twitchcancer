#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
from threading import Thread
import logging
logger = logging.getLogger(__name__)

CYCLE_DURATION = datetime.timedelta(minutes=1)

class Cron(Thread):

  def __init__(self):
    super().__init__()

    self.jobs = []

  #
  # Adds a job to be run
  #
  # - call: function or method
  # - interval: minutes (int) (default: 1)
  # - last_run: datetime (utc) (default: now)
  #
  def add(self, call, interval=1, last_run=datetime.datetime.now(datetime.timezone.utc)):
    job = {
      'call': call,
      'interval': datetime.timedelta(minutes=interval),
      'last_run': last_run
    }

    self.jobs.append(job)
    logger.debug('added job %s', job)

  def run(self):
    while True:
      start = datetime.datetime.now(datetime.timezone.utc)

      # run jobs every job.interval
      for job in self.jobs:
        if start - job['last_run'] > job['interval']:

          # call the job's method or function
          job['call']()

          job['last_run'] = start

      # print some stats for debugging
      duration = datetime.datetime.now(datetime.timezone.utc) - start
      ran = [job for job in self.jobs if job['last_run'] == start]

      logger.info('ran %s jobs in %s', len(ran), duration);
      logger.debug('jobs %s', ran)

      # wait until our next run
      time.sleep((CYCLE_DURATION - duration).total_seconds())

def hello():
  print('hello')

class Hello():

  def hello(self):
    print('hello from %s', self)

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  cron = Cron()

  cron.add(hello)

  hell = Hello()
  cron.add(hell.hello)

  cron.start()

  while True:
    time.sleep(60)
