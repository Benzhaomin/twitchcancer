#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from twitchcancer.chat.irc.threaded import ThreadedIRCMonitor
from twitchcancer.chat.websocket.async import AsyncWebSocketMonitor

# profiling: import yappi

def run(args):
  # profiling: yappi.start()

  if args.protocol == 'irc':
    monitor = ThreadedIRCMonitor(viewers=args.viewers)
  else:
    monitor = AsyncWebSocketMonitor(viewers=args.viewers)

  monitor.run()

  # profiling: yappi.get_func_stats().print_all()
  # profiling: yappi.get_thread_stats().print_all()
