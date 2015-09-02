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
      if t.match(name):
        return t
    logger.warning('no result in find(%s)', name)
    return None

  # check whether name is the name of this topic
  def match(self, name):
    return self.name == name

  # return the topic's current data from cache or freshly computed
  def payload(self, useCache=False, **kwargs):
    if not useCache or self.data is None:
      self.data = self.callback()
    return self.data

# represents a topic where the last part of the path is variable
class PubSubVariableTopic(PubSubTopic):

  def __init__(self, name, callback, sleep):
    super().__init__(name, callback, sleep)

    # cached data can belong to multiple topics depending on our variable
    self.data = {}

    if not self.name.endswith(".*"):
      raise NotImplementedError("regexp topics must end with a variable part")

  # checks whether name is like the name of this topic
  def match(self, name):
    return name.startswith(self.name.replace("*", ""))

  # return the variable part of the path
  def argument(self, name):
    return name[len(self.name.replace("*", "")):]

  # return the topic's current data from cache or freshly computed
  def payload(self, useCache=False, **kwargs):
    if not useCache or self.data is None or kwargs["name"] not in self.data:
      self.data[kwargs["name"]] = self.callback(self.argument(kwargs["name"]))

    return self.data[kwargs["name"]]
