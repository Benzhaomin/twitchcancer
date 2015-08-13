#!/usr/bin/env python
# -*- coding: utf-8 -*-

# abstract cancer source
class Source:

  def __init__(self):
    pass

  def __iter__(self):
    return self

  def __eq__(self, other):
    return self.name() == other.name()

  def __neq__(self, other):
    return self.name() != other.name()

  def name(self):
    return id(self)
