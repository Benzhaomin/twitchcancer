import logging
import os

import yaml

logger = logging.getLogger('twitchcancer')


class Config:
    config = {}

    # update the current config only overwriting new values
    @classmethod
    def update(cls, config_dict):
        cls.config = cls.deep_merge(cls.config, config_dict)

    @classmethod
    def deep_merge(cls, old, new):
        if not isinstance(old, dict):
            if not isinstance(new, dict):
                return new
            else:
                return old
        else:
            if isinstance(new, dict):
                for key in old:
                    if key in new:
                        old[key] = cls.deep_merge(old[key], new[key])
                return old
            else:
                return old

    # load config from a yaml file
    @classmethod
    def load(cls, path):
        logger.debug("loading config from %s", path)

        # read the yaml config file
        with open(path, 'r') as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)

        # merge this config with the default one
        cls.update(yaml_config)

    # load defaults
    @classmethod
    def defaults(cls, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "config.default.yml")
        with open(path, 'r') as yaml_file:
            cls.config = yaml.safe_load(yaml_file)

    # returns a single value of the configuration
    @classmethod
    def get(cls, key):
        config = cls.config
        for level in key.split('.'):
            config = config.get(level, {})
        return config


Config.defaults()

specific_config = os.getenv('TWITCHCANCER_CONFIGFILE')
if specific_config:
    Config.load(specific_config)
