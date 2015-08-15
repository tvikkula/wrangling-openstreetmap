from pymongo import MongoClient
import codecs

client = MongoClient("mongodb://localhost:27017/")

db = client['osm']

hesa = db.hesa
# Write all unique keys in hesa-collection to hesa-keys.txt:
with codecs.open("../data/hesa-keys.txt", "w") as fo:
    fo.write('\n'.join(reduce(lambda all_keys, rec_keys: all_keys | set(rec_keys), map(lambda d: d.keys(), hesa.find()), set())).encode('utf-8'))
