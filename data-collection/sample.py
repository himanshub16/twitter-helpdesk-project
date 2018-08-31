# coding: utf-8
from pymongo import MongoClient
db = MongoClient().get_database('summer-project')
import json
with open('./data/flipkartsupport-2017-12-31.json') as f:
    flipkart_orig = json.loads(f.read())
    
flipkart = list(db.tweets.find({'in_reply_to_status_id_str': {'$ne': None}, 'user.screen_name': 'flipkartsupport'}))
all_ids = [each['id_str'] for each in flipkart]
orig_ids = [each['tweet_id'] for each in flipkart_orig]
all_ids = set(all_ids)
orig_ids = set(orig_ids)
diff_ids = orig_ids.difference(all_ids)
diff_ids = list(diff_ids)
diff_ids[0]
len(flipkart)
len(all_ids)
len(diff_ids)
gmail = list(db.tweets.find({'in_reply_to_status_id_str': {'$ne': None}, 'user.screen_name': 'gmail'}))
ola = list(db.tweets.find({'in_reply_to_status_id_str': {'$ne': None}, 'user.screen_name': 'ola_supports'}))
uber = list(db.tweets.find({'in_reply_to_status_id_str': {'$ne': None}, 'user.screen_name': 'UberINSupport'}))
len(flipkart) + len(gmail) + len(ola)+  len(uber)
p_flipkart = [each['in_reply_to_status_id_str'] for each in flipkart]
p_ola = [each['in_reply_to_status_id_str'] for each in ola]
p_gmail = [each['in_reply_to_status_id_str'] for each in gmail]
p_uber = [each['in_reply_to_status_id_str'] for each in uber]
len(p_flipkart)
pool = p_flipkart + p_ola + p_gmail + p_uber
len(pool)
pool[0]
pool = set(pool)
mainpool = flipkart + uber + ola + gmail
mainpool[0]['id_str']
mainpool_id = set([each['id_str'] for each in mainpool])
mainpool_id.difference(pool)
print(len(mainpool_id.difference(pool)))
print(len(pool.difference(mainpool_id)))
