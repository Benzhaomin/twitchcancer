#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

# represents a topic, roughly a data type/view on the model accessible on the socket
class PubSubTopic:

  # keep track of all instances to be able to find them by name later
  # TODO: have any other mechanism handle that job (pass object, singleton, etc)
  instances = set()

  # init a PubSubTopic with its name, callback to get data from and sleep duration between cycles
  def __init__(self, name, callback, sleep):
    self.name = name
    self.callback = callback
    self.sleep = sleep
    self.data = None

    # TODO: remove on destroy
    PubSubTopic.instances.add(self)

  # evaluates to the path (eg. "twitchcancer.live")
  def __str__(self):
    return self.name

  # find a topic by name
  def find(name):
    for t in PubSubTopic.instances:
      if t.name == name:
        return t
    logger.warn('no result in find(%s)', name)
    return None

  # return the topic's current data from cache or freshly computed
  def payload(self, useCache=False):
    if not useCache:
      self.data = self.callback()
    return self.data

