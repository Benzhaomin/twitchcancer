# TwitchCancer

Diagnose and cure Twitch chat's cancer by removing spam and non-sensical stuff.

Monitoring and recording historical cancer levels is also possible.

## Requirements

- irc: https://pypi.python.org/pypi/irc

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

# License

> TwitchCancer, a Python 3 toolbox to diagnose, monitor and cure chat cancer on Twitch.
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
