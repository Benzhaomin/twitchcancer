#!/usr/bin/env python
# -*- coding: utf-8 -*-

def run(args):
  # lazy import to avoid hard-depending on all the websocket stuff
  from twitchcancer.api.websocketapi import run as websocketrun
  websocketrun(args)
