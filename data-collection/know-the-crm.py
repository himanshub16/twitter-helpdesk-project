# coding: utf-8
import tweepy
import json
with open('./env.json') as f:
    env = json.loads(f.read())['twitter_creds']

auth = tweepy.OAuthHandler(env['consumer_key'], env['consumer_secret'])
auth.set_access_token(env['access_token'], env['access_token_secret'])
api = tweepy.API(auth)

with open('./crm-query.txt') as f:

    screen_names = f.readlines()

result = {}
for each in screen_names:
    result[each] = list(set(map(lambda x: x.source, api.user_timeline(screen_name=each, count=10))))

with open('twitter-clients.json', 'w') as f:
    f.write(json.dumps(result))
