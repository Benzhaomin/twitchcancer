# TwitchCancer

Suite of tool targeted at diagnosing, monitoring and recording data about chat cancer on Twitch.

These 4 components run independently from each other and communicate through ZeroMQ sockets and WebSockets. Any single one can be restarted or down, the others will reconnect when possible.

## Monitor

### Goal

- join chat channels on Twitch (IRC or WebSocket)
- compute cancer points for each message based on a cancer diagnosis
- store these in-memory and publish reports every minute on a ZeroMQ socket

### Requirements

- IRC: https://pypi.python.org/pypi/irc
or
- Asyncio (Python 3.4+)
- AutoBahn: http://autobahn.ws/python

- PyZMQ: https://github.com/zeromq/pyzmq

### Usage

See `python scripts/monitor.py -h`

## Record

### Goal

- subscribe to the monitoring socket
- update persistent leaderboards with new data (MongoDB)

### Requirements

- PyMongo: https://pypi.python.org/pypi/pymongo
- PyZMQ: https://github.com/zeromq/pyzmq

### Usage

See `python scripts/record.py -h`

## Expose

### Goal

- push live cancer status (every second) and leaderboards (every minute), Pub/Sub WebSocket API

### Usage

See `python scripts/api.py -h`

- connect to: 'ws://localhost:8080'
- subscribe: `{'subscribe': 'topic'}'
- unsubscribe: `{'unsubscribe': 'topic'}'

### Requirements

- PyMongo: https://pypi.python.org/pypi/pymongo
- PyZMQ: https://github.com/zeromq/pyzmq


## Explore

### Goal

- website to display live data (AngularJS)
- subscribe to the Pub/Sub API to always be up-to-date

### Requirements

- grunt

### Usage

TODO

# License

> TwitchCancer, a Python 3 toolbox to diagnose, monitor, record and cure chat cancer on Twitch.
> Copyright (C) 2015 Benjamin Maisonnas

> This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

> This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

> You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.en.html>.
