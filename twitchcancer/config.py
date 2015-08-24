#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer')

import yaml

class Config:

  config = {}

  # load config from a yaml file
  @classmethod
  def load(cls, path):
    logger.debug("loading config from %s", path)

    # read the yaml config file
    with open(path, 'r') as yaml_file:
      yaml_config = yaml.load(yaml_file)

    # merge this config with the default one
    cls.config.update(yaml_config)

  # returns a single value of the configuration
  @classmethod
  def get(cls, key):
    config = cls.config
    for level in key.split('.'):
        config = config.get(level, {})
    return config

Config.load("config.default.yml")
