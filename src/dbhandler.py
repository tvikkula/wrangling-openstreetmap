from pymongo import MongoClient
import pprint

client = MongoClient("mongodb://localhost:27017/")

db = client['osm']

coll = db.hesa

pprint.pprint(coll.find_one())
