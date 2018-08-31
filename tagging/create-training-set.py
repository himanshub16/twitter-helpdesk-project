#!/usr/bin/env python3

import sys
import os
from pymongo import MongoClient
from pprint import pprint

DB_NAME = 'not-truncated'
CONVERSATION_COLL = 'conversations'


def get_tagged_conversations(screen_name, db):
    convs = db.conversations.find({'screen_name': screen_name, 'topics': {'$ne': []}})
    tagged = []
    for c in convs:
        for m in c['messages']:
            if m['important']:
                tagged.append((m['processed_text'].replace('\n', ''), c['topics']))

    return tagged


def create_training_set(tagged_convs, filename):
    with open(filename, 'w') as f:
        for msg, topics in tagged_convs:
            txt = ' '.join(['__label__'+t for t in topics]) + ' ' + msg + os.linesep
            f.write(txt)


def main():
    screen_name = sys.argv[1]
    db = MongoClient().get_database(DB_NAME)
    print(screen_name)
    tagged_ones = get_tagged_conversations(screen_name, db)
    # pprint(tagged_ones)
    create_training_set(tagged_ones, 'conversations.all.txt')


if __name__ == '__main__':
    main()
