# TwitchCancer

Toolbox targeted at diagnosing, curing, monitoring and recording historical data
about chat cancer on Twitch.

## Requirements

For any live channel feature:
- IRC: https://pypi.python.org/pypi/irc

To monitor and get the history of a channel:
- PyMongo: https://pypi.python.org/pypi/pymongo

To expose the history of a channel over HTTP:
- Bottle: https://pypi.python.org/pypi/bottle

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

### HTTP API

JSON API exposing historical records and live level of cancer per channel.

- run: `python twitchcancer/main.py history`
- query: `curl 'http://localhost:8080/history/summit1g?interval=60'
- query: `curl 'http://localhost:8080/cancer/summit1g?horizon=60'

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
