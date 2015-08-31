
from setuptools import setup, find_packages

# modular dependencies
scripts = set()
requires = set(['pyzmq >=14.7.0', 'PyYAML >= 3.11'])
extras_requires = {'monitor': set(), 'record': set(), 'expose': set()}
test_requires = set()
excludes = set('tests')
package_data = {'twitchcancer': ['config.default.yml']}

libs = {
  'pymongo': 'pymongo >= 3.0.3',
  'autobahn': 'autobahn >= 0.10.5',
  'irc': 'irc >= 11.0.1',
}

# Monitor
scripts.add('scripts/twitchcancer-monitor')

# packages
# ("twitchcancer.chat")
# ("twitchcancer.chat.*")
# ("twitchcancer.monitor")
# ("twitchcancer.symptom")

# web-sockets need autobahn
extras_requires['monitor'].add(libs['autobahn'])
test_requires.add(libs['autobahn'])

# irc needs irc
extras_requires['monitor'].add(libs['irc'])

# diagnosis needs a list of emotes
package_data['twitchcancer.symptom'] = ['emotes.txt', 'banned.txt']

# Record
scripts.add('scripts/twitchcancer-record')

# persistent storing needs mongodb
extras_requires['record'].add(libs['pymongo'])

# Expose
scripts.add('scripts/twitchcancer-expose')

# packages
# ("twitchcancer.api")

# persistent storing needs mongodb
extras_requires['expose'].add(libs['pymongo'])

# web-sockets need autobahn
extras_requires['expose'].add(libs['autobahn'])

'''
print("scripts", scripts)
print("requires", requires)
print("excludes", excludes)
print("extras_requires", extras_requires)
print("tests_require", test_requires)
'''

# setup
setup(
  name = 'twitchcancer',
  version = '0.1.4',
  packages = find_packages(exclude=excludes),
  scripts = scripts,
  package_data = package_data,
  test_suite = 'tests',
  install_requires = requires,
  extras_require = extras_requires,
  tests_require = test_requires,

  # metadata
  author = 'Benjamin Maisonnas',
  author_email = 'ben@wainei.net',
  description = 'Suite of tools to monitor and analyze chat cancer in Twitch chatrooms.',
  license = 'GPLv3',
  #keywords = "",
  url = 'http://github.com/benzhaomin/twitchcancer',
)
