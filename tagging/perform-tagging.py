#!/usr/bin/env python3

import json
import sys
from pymongo import MongoClient


DB_NAME = 'not-truncated'
TOPIC_COLL = 'topics'
CONVERSATION_COLL = 'conversations'


def setupIndexes(db):
    topics = db.get_collection(TOPIC_COLL)
    topics.create_index('topic_name', background=True)
    topics.create_index('screen_name', background=True)

    conversations = db.get_collection(CONVERSATION_COLL)
    conversations.create_index('conversation_id', background=True, unique=True)
    conversations.create_index('screen_name', background=True)
    conversations.create_index('messages._id', background=True)
    conversations.create_index('messages.id', background=True)
    conversations.create_index('topics', background=True)
    conversations.create_index('message.important', background=True)


def process_text(tweet):
    text = tweet['full_text']
    # remove entities one by one
    cuts = []
    # # 1. urls
    # cuts.extend(each['indices'] for each in tweet['entities']['urls'])
    # # 2. mentions
    # cuts.extend(each['indices'] for each in tweet['entities']['hashtags'])
    # # 3. hashtags
    # cuts.extend(each['indices'] for each in tweet['entities']['user_mentions'])

    # remove all entities present
    for entity in tweet['entities'].values():
        for each in entity:
            cuts.append(each['indices'])

    cuts_sorted = sorted(cuts, key=lambda x: x[0])
    newtext = ''
    for i, cut in enumerate(cuts_sorted):
        _, y_prev = (0, 0) if i == 0 else cuts_sorted[i-1]
        x, y = cut
        x_next, _ = (-1, -1) if i == len(cuts_sorted)-1 else cuts_sorted[i+1]
        newtext += (text[y_prev:x] + text[y:x_next]).strip()

    return newtext


def populate_conversations(screen_name, json_file, db):
    with open(json_file) as f:
        content = json.loads(f.read())

    all_ids = set(content.keys())
    available_convs = db.get_collection('conversations').find(
        {'screen_name': screen_name},
        {'conversation_id': True})
    available_ids = set(each['conversation_id'] for each in available_convs)
    remaining = all_ids.difference(available_ids)

    if not remaining:
        return

    print()
    print('----', screen_name, '----')
    print('total read :', len(all_ids))
    print('available :', len(available_ids))
    print('remaining :', len(remaining))

    to_insert = [
        {'conversation_id': conv_id,
         'screen_name': screen_name,
         'topics': [],
         'messages': [
             {'_id': msg['_id'],
              'id': msg['id'],
              'screen_name': msg['user']['screen_name'],
              'full_text': msg['full_text'],
              'processed_text': process_text(msg),
              'important': False
             } for msg in content[conv_id]
         ]
        } for conv_id in remaining
    ]

    for i, each in enumerate(to_insert):
        db.get_collection(CONVERSATION_COLL).insert_one(each)
        print('\rInserting (', i+1, ' / ', len(remaining), ')', end='')
    print()

    del content, all_ids, available_convs, available_ids, remaining
    # print(db.conversations.insert_many(to_insert))


def show_topics(topics):
    for i, t in enumerate(topics):
        print('[', i+1, '] ', t, end='  ', sep='')
    print()


def do_it_for_one(conv, topics, db):
    for i, msg in enumerate(reversed(conv['messages']), 1):
        print('[', i, ']', msg['screen_name'], ':', msg['full_text'])
        # print(msg['full_text'])
        print()

    print("Select topics:", end=' ')
    while True:
        show_topics(topics)
        ts = input('Enter apt topics :')
        if ts == 'n':
            newt = input('Topic name: ')
            if newt in topics:
                print("Don't play here. :/")
            else:
                db.get_collection(TOPIC_COLL).insert_one(
                    {'screen_name': conv['screen_name'], 'topic': newt}
                )
                topics.append(newt)
        else:
            break

    for t in map(int, ts.split()):
        conv['topics'].append(topics[t-1])

    imps = input('Enter important messages: ')
    for i in map(int, imps.split()):
        conv['messages'][-1*i]['important'] = True
    # print(ts.split(' '))


def perform_tagging(screen_name, db):
    topics = [each['topic'] for each in db.get_collection(TOPIC_COLL).find({'screen_name': screen_name})]
    conversations = db.get_collection(CONVERSATION_COLL)
    n_untagged = conversations.count({
        'screen_name': screen_name,
        'topics': {'$size': 0}
    })
    n_tagged = conversations.count({
        'screen_name': screen_name,
        # '$where': 'this.topics.length > 0',
        'topics': {'$ne': []}
    })
    print('----', screen_name, '----')
    print('stats:')
    print('topics :', len(topics))
    print(topics)
    print('Tagging status :', n_tagged, '/', n_untagged+n_tagged)
    print()

    print('Starting tagging... Press ctrl+c to break it')

    i = 1 + n_tagged
    # for i, conv in enumerate(conversations.find({'topics': {'$size': 0},'screen_name': screen_name}), n_tagged+1):
    while True:
        conv = conversations.find_one({'topics': {'$size': 0}, 'screen_name': screen_name, 'locked': False})
        conversations.update_one({'_id': conv['_id']}, {'$set': {'locked': True}})
        print()
        print(i, '/', n_tagged+n_untagged, ' :: ', conv['_id'])
        do_it_for_one(conv, topics, db)
        conversations.update_one({'_id': conv['_id']}, {'$set': {'topics': conv['topics'], 'messages': conv['messages'], 'locked': False}})
        print('topics selected : ', conv['topics'], 'important :', [each['important'] for each in reversed(conv['messages'])])
        print('-'*30)
        i += 1



def main():
    db = MongoClient().get_database(DB_NAME)
    setupIndexes(db)
    # populate_conversations('flipkartsupport', './data/flipkartsupport.json', db)
    # populate_conversations('ola_supports', './data/ola_supports.json', db)
    # populate_conversations('UberINSupport', './data/UberINSupport.json', db)
    # populate_conversations('gmail', './data/gmail.json', db)

    screen_name = sys.argv[1]
    perform_tagging(screen_name, db)


if __name__ == '__main__':
    main()
