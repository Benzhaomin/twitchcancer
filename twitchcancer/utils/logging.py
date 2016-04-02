#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging.handlers

def setup_logger(logger, log_level, config, logfile_name):

  # set log level
  if log_level is None:
    log_level = config.get("logging.level")

  numeric_level = getattr(logging, log_level.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % log_level)

  # set log handler/destination
  log_output = config.get("logging.output")

  if (log_output != "stderr"):
    logfile_path = os.path.join(log_output, logfile_name)
    handler = logging.FileHandler(logfile_path)
  else:
    handler = logging.StreamHandler()

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  handler.setLevel(numeric_level)

  logger.addHandler(handler)
  logger.setLevel(numeric_level)
  logger.debug("Set up logger on %s", log_output)
