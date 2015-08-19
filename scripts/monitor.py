#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer')

from twitchcancer.chat.chat import run

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # persist data generated by monitor

  parser.add_argument('--log', dest='loglevel', default='WARNING',
    help="set the level of messages to display")

  parser.add_argument('--viewers', dest='viewers', default=1000, type=int,
    help="minimum viewer count to monitor channels (default: 1000)")

  parser.add_argument("--protocol", dest="protocol", default="websocket",
    help="protocol to use to monitor chat channels, websocket or irc (default: websocket)")
  #parser.add_argument("--pub-socket", dest="pub-socket", default="ipc:///tmp/twitchcancer-pubsub-summary.sock", help="URI of the pub/sub socket (default: ipc:///tmp/twitchcancer-pubsub-summary.sock)")
  #parser.add_argument("--req-socket", dest="req-socket", default=ipc:///tmp/twitchcancer-read-cancer.sock, help="URI of the req/rep socket (default: ipc:///tmp/twitchcancer-read-cancer.sock)")

  args = parser.parse_args()

  # set logger level
  numeric_level = getattr(logging, args.loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger.setLevel(numeric_level)

  # start recording forever
  run(args)

