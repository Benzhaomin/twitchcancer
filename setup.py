
import sys
from setuptools import setup, find_packages

# modular dependencies
scripts = []
requires = ['pyzmq >=14.7.0', 'PyYAML >= 3.11']
extras_requires = []
excludes = []
package_data = {}

libs = {
  'pymongo': 'pymongo >= 3.0.3',
  'autobahn': 'autobahn >= 0.10.5',
  'irc': 'irc >= 11.0.1',
}

# with or without chat monitoring
if "--no-monitor" not in sys.argv:
  # main script
  scripts.append('scripts/twitchcancer-monitor')

  # web-sockets need autobahn
  extras_requires.append(libs['autobahn'])

  # irc needs irc
  extras_requires.append(libs['irc'])

  # diagnosis needs a list of emotes
  package_data['twitchcancer.symptom'] = ['emotes.txt']
else:
  excludes.append("twitchcancer.chat")
  excludes.append("twitchcancer.chat.*")
  excludes.append("twitchcancer.monitor")
  excludes.append("twitchcancer.symptom")

  sys.argv.remove("--no-monitor")

# with or without API
if "--no-expose" not in sys.argv:
  # main script
  scripts.append('scripts/twitchcancer-expose')

  # persistent storing needs mongodb
  if libs['pymongo'] not in requires:
    requires.append(libs['pymongo'])

  # web-sockets need autobahn
  requires.append(libs['autobahn'])

  # autobahn is not just extra anymore
  if libs['autobahn'] in extras_requires:
    extras_requires.remove(libs['autobahn'])
else:
  excludes.append("twitchcancer.api")

  sys.argv.remove("--no-expose")

# with or without cancer levels recording
if "--no-record" not in sys.argv:
  # main script
  scripts.append('scripts/twitchcancer-record')

  # persistent storing needs mongodb
  if libs['pymongo'] not in requires:
    requires.append(libs['pymongo'])
else:
  sys.argv.remove("--no-record")

print("scripts", scripts)
print("requires", requires)
print("excludes", excludes)
print("extras_requires", extras_requires)

# setup
setup(
  name = 'twitchcancer',
  version = '0.0.1',
  packages = find_packages(exclude=excludes),
  scripts = scripts,
  install_requires = requires,
  package_data = package_data,
  test_suite = 'tests',

  # metadata
  author = 'Benjamin Maisonnas',
  author_email = 'ben@wainei.net',
  description = 'Suite of tools to monitor and analyze Twitch chatrooms.',
  license = 'GPLv3',
  #keywords = "",
  url = 'http://github.com/benzhaomin/twitchcancer',
)


