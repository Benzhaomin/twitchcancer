#!/usr/bin/env python
# -*- coding: utf-8 -*-

class StorageInterface:

  def __init__(self):
    pass

  # returns live cancer levels
  def cancer(self):
    raise NotImplementedError()

  # returns all the leaderboards
  def leaderboards(self):
    raise NotImplementedError()

  # returns a full leaderboard
  def leaderboard(self, leaderboard):
    raise NotImplementedError()

  # returns best scores and leaderboard ranks of a channel
  def channel(self, channel):
    raise NotImplementedError()

  # returns an overview of the current status of both the db and the monitoring process
  def status(self):
    raise NotImplementedError()

  # stores a message and its cancer points
  def store(self, channel, cancer):
    raise NotImplementedError()

  # start persisting message summaries
  def record(self):
    raise NotImplementedError()

  # search for a channel based on part of its name
  def search(self, root):
    raise NotImplementedError()
