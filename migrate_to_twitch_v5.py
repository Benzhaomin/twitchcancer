""" Add Twitch channel id to leaderboards
"""
import sys

from twitchcancer.storage.persistentstore import PersistentStore
from twitchcancer.utils.twitchapi import TwitchApi

if __name__ == '__main__':
    store = PersistentStore()
    leaderboards = store.db.leaderboard.find({'channel': {'$regex': '#.*'}}, limit=100)
    names = [leaderboard['channel'].replace('#', '') for leaderboard in leaderboards]
    if not names:
        print('Nothing to migrate')
        sys.exit()

    users = TwitchApi.request('https://api.twitch.tv/kraken/users?login=' + ','.join(names))["users"]
    for user in users:
        channel_name = user['name']
        channel_id = user['_id']

        query = {'channel': '#' + channel_name}
        update = {'$set': {'channel': channel_name, 'channel_id': channel_id}}
        print('Migrating {} to {}'.format(channel_name, channel_id))

        store.db.daily_leaderboard.update_one(query, update)
        store.db.monthly_leaderboard.update_one(query, update)
        store.db.leaderboard.update_one(query, update)
        names.remove(channel_name)

    for name in names:
        print('Failed to find channel id for channel {}'.format(name))
