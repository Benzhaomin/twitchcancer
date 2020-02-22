#!/usr/bin/env python

import argparse
import logging

from twitchcancer.config import Config
from twitchcancer.utils.logging import setup_logger

logger = logging.getLogger('twitchcancer')


def main():
    # monitor chat channels
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='loglevel',
                        help="set the level of messages to display")
    parser.add_argument('-c', '--config', dest='config',
                        help="load configuration from this file")
    parser.add_argument('--viewers', dest='viewers', default=0, type=int,
                        help="minimum viewer count to monitor channels (default: 0)")

    args = parser.parse_args()
    if args.config:
        Config.load(args.config)
    setup_logger(logger, args.loglevel, Config, "monitor.log")

    # start monitoring forever
    from twitchcancer.chat.chat import run

    run(args)


if __name__ == "__main__":
    main()
