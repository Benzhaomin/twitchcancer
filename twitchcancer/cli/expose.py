#!/usr/bin/env python

import argparse
import logging

from twitchcancer.config import Config
from twitchcancer.utils.logging import setup_logger

logger = logging.getLogger('twitchcancer')


def main():
    # run the websocket API
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='loglevel',
                        help="set the level of messages to display")
    parser.add_argument('-c', '--config', dest='config',
                        help="load configuration from this file")

    args = parser.parse_args()
    if args.config:
        Config.load(args.config)

    setup_logger(logger, args.loglevel, Config, "expose.log")

    # start running the api forever
    from twitchcancer.api.websocketapi import run

    run(args)


if __name__ == "__main__":
    main()
