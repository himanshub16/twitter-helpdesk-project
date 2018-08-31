#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timedelta
from businesshours import BusinessHours
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--twitter-id', help='twitter page to work for',
                        required=True)
    parser.add_argument('-f', '--conversation-file', help='file having the conversations', required=True)
    parser.add_argument('-o', '--outfile', help='resulting json file')
    parser.add_argument('-v', '--verbose', help='log everything',
                        action='store_false')
    return parser.parse_args()


def get_conversations(filename):
    with open(filename) as f:
        content = json.loads(f.read())
    return content


def split_conversations_to_interactions(conv, org_name):
    splitted = []
    missed = []
    marked = {}
    for c in conv.values():
        here = {t['id_str']: t
                for t in c}
        for t in here.values():
            if t['user']['screen_name'] == org_name:
                # avoid duplicates if crept out
                if t['id_str'] not in marked:
                    marked[t['id_str']] = True
                # avoid key error (if crept out)
                if t['in_reply_to_status_id_str'] in here:
                    splitted.append((t, here[t['in_reply_to_status_id_str']]))
                else:
                    missed.append(t)

    return splitted, missed


def get_sentiment(text):
    "TODO"
    return 0.8


def has_profanity(text):
    "TODO"
    return True


def prepare_features(conversations):
    features = []
    parse_ts = lambda ts: datetime.strptime(ts, '%a %b %d %H:%M:%S +0000 %Y')
    in_business_hours = lambda d: d.hour > 9 and d.hour < 20
    ist = lambda d: d + timedelta(hours=5, minutes=30)
    # orgt - org's tweet, cust - customer's tweet
    for orgt, cust in conversations:
        # import pdb; pdb.set_trace()
        created_at = parse_ts(cust['created_at'])
        responded_at = parse_ts(orgt['created_at'])
        here = {
            # the result
            'responded_in': (responded_at-created_at).total_seconds(),
            'responded_in_bh': BusinessHours(ist(created_at), ist(responded_at)).total_seconds,

            # tweet info
            'tweet_length': len(cust['full_text']),
            'n_hashtags': len(cust['entities']['hashtags']),
            'n_mentions': len(cust['entities']['user_mentions']),
            'n_links': len(cust['entities']['urls']),
            'source': cust['source'].split('>')[1].split('<')[0],

            'ratio_hashtags': sum(map(lambda h: h['indices'][1]-h['indices'][0],
                                      cust['entities']['hashtags']
                                     )) / len(cust['full_text']),

            'ratio_user_mentions': sum(
                map(lambda h: h['indices'][1]-h['indices'][0],
                    cust['entities']['user_mentions'])
            ) / len(cust['full_text']),

            'created_at_hour': ist(created_at).hour,
            'responded_at_hour': ist(responded_at).hour,
            'retweet_count': cust['retweet_count'],
            'favorite_count': cust['favorite_count'],

            # derived attribute
            'ratio_numeric': sum(map(str.isnumeric, cust['full_text'])) / len(cust['full_text']),
            'in_business_hours': int(in_business_hours(ist(created_at))),
            'sentiment': get_sentiment(cust['full_text']),
            'has_profanity': int(has_profanity(cust['full_text'])),

            # user info
            'protected': int(cust['user']['protected']),
            'n_followers': cust['user']['followers_count'],
            'n_following': cust['user']['friends_count'],
            'n_favorites': cust['user']['favourites_count'],
            'verified': int(cust['user']['verified']),
            'n_statuses': cust['user']['statuses_count'],
            'user_age': (created_at - parse_ts(cust['user']['created_at'])).total_seconds(),

            'cust_tid': cust['id_str'],
            'org_tid': orgt['id_str']
            }

        features.append(here)

    return features


def do_it_for_one(twitter_id):
    print(twitter_id)
    conversations = get_conversations('./data/'+twitter_id+'.json')
    print(len(conversations))
    splitted, missed = split_conversations_to_interactions(conversations, twitter_id)
    print(len(splitted), len(missed))
    features = prepare_features(splitted)
    print(len(features))
    df = pd.DataFrame.from_dict(features)
    return df


def main():
    # args = parse_args()
    # conversations = get_conversations(args.conversation_file)
    # print(len(conversations))
    # splitted, missed = split_conversations_to_interactions(conversations, args.twitter_id)
    # print(len(splitted), len(missed))
    # features = prepare_features(splitted)
    # print(len(features))
    # df = pd.DataFrame.from_dict(features)
    # df.to_csv('features-' + args.twitter_id + '.csv')

    writer = pd.ExcelWriter('./features/features.xlsx')
    for twitter_id in ['flipkartsupport', 'ola_supports', 'UberINSupport', 'gmail']:
        df = do_it_for_one(twitter_id)
        df.to_csv('./features/features-'+twitter_id+'.csv')
        df.to_excel(writer, twitter_id)

    # df.to_excel(writer, args.twitter_id)
    writer.save()


if __name__ == '__main__':
    main()
