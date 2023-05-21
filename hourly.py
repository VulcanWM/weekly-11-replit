import pymongo
import os
import dns
client = pymongo.MongoClient(os.getenv("clientm"))
usersdb = client.Users
profilescol = usersdb.Profiles
hourlycol = usersdb.Hourly

def some_job():
    hourly = {"_id": 1}
    hourlycol.delete_one(hourly)
    hourlycol.insert_many([{"_id": 1, "Hourly": True}])
    for uservalue in profilescol.find():
      if uservalue['Hourly'] > 0:
        user2 = uservalue
        newam = user2['Money'] + uservalue['Hourly']
        del user2['Money']
        user2['Money'] = newam
        delete = {"_id": uservalue['_id']}
        profilescol.delete_one(delete)
        profilescol.insert_many([user2])
    hourlycol.delete_one(hourly)
    hourlycol.insert_many([{"_id": 1, "Hourly": False}])