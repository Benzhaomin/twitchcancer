
diagnosis
  cancer points
    symptoms award cancer points
      eg. EmotesCount: 3 for first 5 emotes, 1 afterwards

api
  live == websocket
    update every 3 seconds by map reduce into a DB collection, pushed on the websocket

  leaderboards
    total cancer, sort by count
    total cancer per minute, sort by count

    total cancer per message, sort by count
    total cancer per message, sort by count

    total messages, sort by count
    total messages in 5 minutes, sort by count

db
  pymongo.errors.AutoReconnect: connection closed
