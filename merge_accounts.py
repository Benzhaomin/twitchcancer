""" Merge an old_account's data with a new one after a channel name change
"""
import sys

from twitchcancer.storage.persistentstore import PersistentStore

if __name__ == '__main__':
    store = PersistentStore()

    current_account_query = {'channel': sys.argv[1]}
    current_account = store.db.leaderboard.find_one(current_account_query)
    if not current_account:
        print('current account not found', current_account_query)
        sys.exit(1)

    old_account_query = {'channel': sys.argv[2]}
    old_account = store.db.leaderboard.find_one(old_account_query)
    if not old_account:
        print('old account not found', old_account_query)
        sys.exit(1)

    update = {
        '$set': {
            'total.cancer': current_account['total']['cancer'] + old_account['total']['cancer'],
            'total.messages': current_account['total']['messages'] + old_account['total']['messages'],
            'average.duration': current_account['average']['duration'] + old_account['average']['duration'],

            'average.cancer': (current_account['total']['cancer'] + old_account['total']['cancer']) /
                              (current_account['average']['duration'] + old_account['average']['duration']),

            'average.messages': (current_account['total']['messages'] + old_account['total']['messages']) /
                                (current_account['average']['duration'] + old_account['average']['duration']),

            'average.cpm': (current_account['total']['cancer'] + old_account['total']['cancer']) /
                           (current_account['total']['messages'] + old_account['total']['messages']) /
                           (current_account['average']['duration'] + old_account['average']['duration']),

            'total.cpm': (current_account['total']['cancer'] + old_account['total']['cancer']) /
                         (current_account['total']['messages'] + old_account['total']['messages']),
        }  # noqa
    }

    # print(old_account)
    # print(current_account)
    # print(current_account_query, update)
    store.db.leaderboard.update_one(current_account_query, update)
    store.db.leaderboard.delete_one(old_account_query)

    store.db.monthlyLeaderboard.update_many(
        old_account_query,
        {'$set': {'channel': sys.argv[1]}}
    )

    store.db.dailyLeaderboard.update_many(
        old_account_query,
        {'$set': {'channel': sys.argv[1]}}
    )
