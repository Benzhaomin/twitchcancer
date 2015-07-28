# TwitchCancer

Diagnose and cure Twitch chat's cancer by removing spam and non-sensical stuff

## Requirements

- irc: https://pypi.python.org/pypi/irc

## Usage

### Diagnose

Runs a diagnosis of a source, prints stats about its cancer status.

- live chat channel: `python twitchcancer/main.py diagnose gamesdonequick`
- log file: `cat chat.log | python twitchcancer/main.py diagnose`

### Cure

Filters cancer messages out of a chat.

- live chat channel: `python twitchcancer/main.py cure gamesdonequick`
- log file: `cat chat.log | python twitchcancer/main.py cure`


