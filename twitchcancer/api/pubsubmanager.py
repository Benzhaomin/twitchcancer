#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import logging
logger = logging.getLogger(__name__)

from twitchcancer.api.pubsubtopic import PubSubTopic

# manage subscriptions from clients and publish messages to them when asked to
class PubSubManager:

  __instance = None

  # poor man's singleton
  def instance():
    if PubSubManager.__instance is None:
      PubSubManager.__instance = PubSubManager()
    return PubSubManager.__instance

  def __init__(self):
    self.subscriptions = collections.defaultdict(set)

  # publish new data to every client subscribed to a topic
  def publish(self, topic):

    # find all the topic by name (pattern matching)
    for topic_name, clients in self.subscriptions.items():

      if topic.match(topic_name):
        # get data for this topic, with its full name in case it contains arguments
        data = topic.payload(name=topic_name)
        logger.debug('publishing data for %s to %s subs', topic_name, len(clients))

        # push new data to every client
        for client in clients:
          client.send(topic_name, data)

  # publish data from a topic to a single client, usually right after subscription
  def publish_one(self, client, topic):
    t = PubSubTopic.find(topic)

    if t:
      logger.debug('publishing data once for %s to %s', topic, client)
      client.send(topic, t.payload(useCache=True, name=topic))

  # let clients subscribe to a single topic
  def subscribe(self, client, topic):
    # remember this client for later publication cycles
    self.subscriptions[topic].add(client)

    logger.debug('subscribed %s to %s', client, topic)

  # let clients unsubscribe from a single topic
  def unsubscribe(self, client, topic):
    try:
      self.subscriptions[topic].remove(client)
      logger.debug('unsubscribed %s from %s', client, topic)

    except KeyError as e:
      logger.warning('unsubscribed %s from %s failed with: %s', client, topic, e)

    # remove empty records
    if len(self.subscriptions[topic]) == 0:
      logger.debug('%s lost its last subscriber, removing it', topic)
      del self.subscriptions[topic]

  # let clients unsubscribe from all topics at once
  def unsubscribe_all(self, client):
    for topic in list(self.subscriptions):
      self.unsubscribe(client, topic)
