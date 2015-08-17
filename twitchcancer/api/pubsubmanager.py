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

  # publish an event to every client subscribed to a topic
  def publish(self, topic, data):
    logger.debug('publishing data for %s to %s subs', topic, len(self.subscriptions[topic]))
    for subscriber in self.subscriptions[topic]:
      subscriber.send(topic, data)

  # publish data from a topic to a single client, usually right after subscription
  def publish_one(self, client, topic):
    t = PubSubTopic.find(topic)

    if t:
      logger.debug('publishing data once for %s to %s', topic, client)
      client.send(topic, t.payload(useCache=True))

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
    except KeyError:
      logger.warn('unsubscribed %s from %s but this topic doesn\'t exist', client, topic)
      pass

  # let clients unsubscribe from all topics at once
  def unsubscribe_all(self, client):
    for topic in list(self.subscriptions):
      self.unsubscribe(client, topic)
