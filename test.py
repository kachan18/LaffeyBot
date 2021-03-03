import pymongo
import datetime

mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % "serveradmin")
#game = mclient.Laffey.Gamble.find_one({"GAME": "BLACKJACK"})

#print(game["LAFFEY"]["ACE"])

# mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": False, "BET": 100, "USERID": 10, "USERNICK": "TESTER", "LAFFEY": {"ACE": False, "COUNT": 0}, "USER": {"ACE": False, "COUNT": 0}}})
authinfo = mclient.Laffey.Data.find_one({"ID": 617216144008282132})
if authinfo["DCTime"] < int(datetime.datetime.now().strftime("%Y%m%d")):
    print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))))
    print(datetime.timezone)
else:
    print("FALSE")
