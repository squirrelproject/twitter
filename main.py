import json
import twint
import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pymongo import MongoClient


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey)) 
            for key, value in obj.__dict__.items() 
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
conn_str = os.getenv("SQUIRREL_MONGO_URI")
client = MongoClient(conn_str)
db = client["tweets"]

c = twint.Config()
c.Username = "twitter"
c.Store_object = True
c.Store_json = True
c.Limit = 20
c.Output = f"data/{c.Username}_{datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', '_').replace(':', '-')}.json"

twint.run.Search(c)

for tweet in twint.output.tweets_list:
    db[c.Username].find_one_and_replace({"id": tweet.id}, todict(tweet), upsert=True)
