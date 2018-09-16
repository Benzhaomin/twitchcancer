# TwitchCancer

Suite of tools targeted at monitoring, recording and exploring chat cancer on Twitch.

4 components run independently from each other and communicate through ZeroMQ sockets and WebSockets.
Any single one can be restarted or down, the others will reconnect when possible.

- monitor: join Twitch chat channels
- record: update leaderboard data in Mongo
- expose: API for leaderboards and live stats
- explore: website to display leaderboards and live stats

## Install

Requires :

- python3 (>= 3.4)
- pipenv

```shell
pipenv sync --dev
pipenv run docker-compose up -d
bin/tests
```

Edit your local config file (see Configuration)

### Configuration

You can use the `-f` or `--config` switch to pass the path of a configuration file overriding any of the [default settings](twitchcancer/config.default.yml).

The monitor module requires a valid Twitch username, an active oauth key and an API Client ID, example:

```yaml
monitor:
    chat:
        username: username      # your twitch username
        password: oauth:key     # http://twitchapps.com/tmi/
        clientid: xxxx          # https://www.twitch.tv/kraken/oauth2/clients/YOURCLIENTID
```

You would then run the monitor module with:

`bin/monitor -f myconfig.yml`

## Monitor

### Goal

- join chat channels on Twitch (IRC or WebSocket)
- compute cancer points for each message based on a cancer diagnosis
- store these in-memory and publish reports every minute on a ZeroMQ socket

### Requirements

- IRC: https://pypi.python.org/pypi/irc
or
- Python >= 3.4 (asyncio)
- AutoBahn: https://autobahn.ws/python

- PyZMQ: https://github.com/zeromq/pyzmq

### Usage

See `bin/monitor -h`

## Record

### Goal

- subscribe to the monitoring socket
- update persistent leaderboards with new data (MongoDB)

### Requirements

- PyMongo: https://pypi.python.org/pypi/pymongo
- PyZMQ: https://github.com/zeromq/pyzmq

### Usage

See `bin/record -h`

### Maintenance

Daily stats can be deleted unless you want to show browsable daily stats or timelines/graphs with daily data points.

The current front-end doesn't do any of that so a great way to clean-up the db goes like this:

```mongo
use twitchcancer
db.daily_leaderboard.find({'date': { "$lt": ISODate("2016-08-01") }}).count()
db.daily_leaderboard.remove({'date': { "$lt": ISODate("2016-08-01") }})
db.runCommand ( { compact: 'daily_leaderboard' } )
```

## Expose

### Goal

- push live cancer status (every second) and leaderboards (every minute), Pub/Sub WebSocket API

### Usage

See `bin/expose -h`

- connect to: 'ws://localhost:8080'
- subscribe: `{'subscribe': 'topic'}'
- unsubscribe: `{'unsubscribe': 'topic'}'

### Requirements

- PyMongo: https://pypi.python.org/pypi/pymongo
- PyZMQ: https://github.com/zeromq/pyzmq


## Explore

Moved to [its own repository](https://github.com/Benzhaomin/TwitchCancerExplore).
