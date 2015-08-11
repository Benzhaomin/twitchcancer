#!/usr/bin/env python
# -*- coding: utf-8 -*-

# abstract cancer source
class Source:

  def __init__(self):
    pass

  def __iter__(self):
    return self

  def name(self):
    return id(self)
