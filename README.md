# TwitchCancer

Toolbox targeted at diagnosing, curing, monitoring and recording historical data
about chat cancer on Twitch.

## Requirements

For any live channel feature:
- IRC: https://pypi.python.org/pypi/irc

To monitor and get the history of a channel:
- PyMongo: https://pypi.python.org/pypi/pymongo
- PyZMQ: https://github.com/zeromq/pyzmq

To expose the live and leaderboard data over websockets:
- autobahn: http://autobahn.ws/python/

## Usage

### Diagnose

Runs a quick diagnosis of a source, prints stats about its cancer status.

- live chat channel: `python twitchcancer/main.py diagnose gamesdonequick`
- log file: `cat chat.log | python twitchcancer/main.py diagnose`

### Cure

Filters cancer messages out of a chat.

- live chat channel: `python twitchcancer/main.py cure gamesdonequick`
- log file: `cat chat.log | python twitchcancer/main.py cure`

### Monitor

Long-running process used to record historical data on cancer level of several channels.

`python twitchcancer/main.py monitor gamesdonequick forsenlol`

### WebSocket API

WebSocket JSON API exposing live activity and leaderboards. Uses a simple Pub/Sub protocol.

- run: `python twitchcancer/main.py api` (see cli help for more options like port, etc)
- connect to: 'ws://localhost:8080'
- subscribe: `{'subscribe': 'topic'}'
- unsubscribe: `{'unsubscribe': 'topic'}'

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
