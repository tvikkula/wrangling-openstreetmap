from pymongo import MongoClient
import codecs

client = MongoClient("mongodb://localhost:27017/")

db = client['osm']

coll = db.hesa
with codecs.open("../data/hesa-keys.txt", "w") as fo:
    fo.write('\n'.join(reduce(lambda all_keys, rec_keys: all_keys | set(rec_keys), map(lambda d: d.keys(), db.hesa.find()), set())).encode('utf-8'))
