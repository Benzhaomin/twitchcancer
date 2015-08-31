
from setuptools import setup, find_packages

# modular dependencies
scripts = set()
requires = set(['pyzmq >=14.7.0', 'PyYAML >= 3.11'])
extras_requires = set()
excludes = set()
package_data = {'twitchcancer': ['config.default.yml']}

libs = {
  'pymongo': 'pymongo >= 3.0.3',
  'autobahn': 'autobahn >= 0.10.5',
  'irc': 'irc >= 11.0.1',
}

## chat monitoring
# main script
scripts.add('scripts/twitchcancer-monitor')

# packages
# ("twitchcancer.chat")
# ("twitchcancer.chat.*")
# ("twitchcancer.monitor")
# ("twitchcancer.symptom")

# web-sockets need autobahn
extras_requires.add(libs['autobahn'])

# irc needs irc
extras_requires.add(libs['irc'])

# diagnosis needs a list of emotes
package_data['twitchcancer.symptom'] = ['emotes.txt', 'banned.txt']

## API
# main script
scripts.add('scripts/twitchcancer-expose')

# packages
# ("twitchcancer.api")

# persistent storing needs mongodb
extras_requires.add(libs['pymongo'])

# web-sockets need autobahn
extras_requires.add(libs['autobahn'])

## cancer levels recording
# main script
scripts.add('scripts/twitchcancer-record')

# persistent storing needs mongodb
extras_requires.add(libs['pymongo'])

print("scripts", scripts)
print("requires", requires)
print("excludes", excludes)
print("extras_requires", extras_requires)

# setup
setup(
  name = 'twitchcancer',
  version = '0.1.3',
  packages = find_packages(exclude=excludes),
  scripts = scripts,
  install_requires = requires,
  package_data = package_data,
  test_suite = 'tests',

  # metadata
  author = 'Benjamin Maisonnas',
  author_email = 'ben@wainei.net',
  description = 'Suite of tools to monitor and analyze chat cancer in Twitch chatrooms.',
  license = 'GPLv3',
  #keywords = "",
  url = 'http://github.com/benzhaomin/twitchcancer',
)


