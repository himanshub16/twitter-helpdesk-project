#!/usr/bin/env python3

from pymongo import MongoClient
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mongodb', help='mongodb server url',
                        default='')
    parser.add_argument('-d', '--dbname', help='mongodb database name',
                        default='summer-project')
    parser.add_argument('-t', '--twitter-id', help='twitter page to work for',
                        required=True)
    parser.add_argument('-o', '--outfile', help='resulting json file')
    parser.add_argument('-v', '--verbose', help='log everything',
                        action='store_false')
    return parser.parse_args()


def do_it_for_one(args, db, each):
    if args.verbose:
        print()
    # graph[each['id_str']] = [each]
    each['_id'] = str(each['_id'])
    result = [each]
    cur = each
    if args.verbose:
        print('Got', each['id_str'])
        print('adding', end=' ')
    while cur['in_reply_to_status_id_str']:
        try:
            # newone = next(db.tweets.find(
            #     {'id_str': cur['in_reply_to_status_id_str']},
            #     {'_id': True,
            #     'in_reply_to_status_id_str': True,
            #     'id_str': True})
            # )
            newone = next(db.tweets.find(
                {'id_str': cur['in_reply_to_status_id_str']},
            ))
            newone['_id'] = str(newone['_id'])
            result.append(newone)
            cur = newone
            if args.verbose:
                print(newone['id_str'], end=' ')
        except StopIteration:
            if args.verbose:
                print('Stop iteration hit')
            cur = {'in_reply_to_status_id_str': None}

    return result


def prepare_graph(args, db):
    graph = {}
    # org_tweets = db.tweets.find({'user.screen_name': args.twitter_id,
    #                              'in_reply_to_status_id_str': {'$ne': None}},
    #                             {'_id': True,
    #                              'in_reply_to_status_id_str': True,
    #                              'id_str': True})
    org_tweets = db.tweets.find({'user.screen_name': args.twitter_id,
                                 'in_reply_to_status_id_str': {'$ne': None}},
                                )

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(do_it_for_one, args, db, each): each['id_str']
                   for each in org_tweets}
        for fut in as_completed(futures):
            graph[futures[fut]] = fut.result()

    with open(args.outfile, 'w') as outfile:
        outfile.write(json.dumps(graph))


def main():
    args = parse_args()
    if not args.outfile:
        args.outfile = args.twitter_id + '.json'

    if args.mongodb:
        db = MongoClient(args.mongodb).get_database(args.dbname)
    else:
        db = MongoClient().get_database(args.dbname)

    print(db, args)

    prepare_graph(args, db)


if __name__ == '__main__':
    main()


