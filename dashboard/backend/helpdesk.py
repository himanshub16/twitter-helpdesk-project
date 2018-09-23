from flask import Flask , jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import bson.json_util
import json
import os

from learning import classify


client = MongoClient()
db = client[os.environ.get('DB_NAME', 'twitter-helpdesk')]

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder='./dist')
CORS(app)

mjsonify = lambda obj: jsonify(json.loads(bson.json_util.dumps(obj)))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def frontend(path):
    return render_template('index.html')


@app.route('/api/<screen_name>/')
def dashboard(screen_name):
    user_info = next(db.tweets.find({'user.screen_name':screen_name},{'user':1}).sort('created_at',1).limit(1))
    return mjsonify(user_info)


@app.route('/api/<screen_name>/topics')
def get_topics(screen_name):
    topics = [each['topic'] for each in db.topics.find({'screen_name': screen_name})]
    return mjsonify(topics)


@app.route('/api/<screen_name>/conversations')
def conversations(screen_name):
    topic = request.args.get('topic')
    query = {'screen_name': screen_name}
    if topic:
        query['topics'] = {'$in': [topic]}
    convo = list(db.conversations.find(query).limit(15))
    count = db.conversations.count(query)
    msg_texts = [each['messages'][-1]['processed_text'] for each in convo]
    pred_tags = classify(msg_texts)
    response = []
    for each, tag in zip(convo, pred_tags):
        num_of_interactions = (len(each['messages']))
        first_message_id = (each['messages'][-1]['_id'])
        first_tweet = db.tweets.find_one({'_id':ObjectId(first_message_id)})
        first_tweet['processed_text'] = each['messages'][-1]['processed_text']
        each['n_interacations'] = num_of_interactions
        each['tweet'] = first_tweet
        each['suggested_topic'] = tag
        del each['messages']
        response.append(each)

    return mjsonify({'count': count, 'conversations': response})


@app.route('/api/conversations/<conv_id>')
def conversation(conv_id):
    convo = db.conversations.find_one({'_id' : ObjectId(conv_id)})
    ob_ids = [ObjectId(each['_id']) for each in convo['messages']]
    tweets = db.tweets.find({'_id' : {'$in' : ob_ids}})
    t_map = {each['_id'] : each for each in tweets}
    ord_tweets = [t_map[each] for each in reversed(ob_ids)]
    del convo['messages']
    convo['tweets'] = ord_tweets
    return mjsonify(convo)


@app.route('/api/conversations/<conv_id>/topics', methods=['PUT'])
def update_topics(conv_id):
    newtopics = request.get_json().get('topics')
    if not newtopics:
        return 'no topic found', 400
    db.conversations.update_one({'_id': ObjectId(conv_id)},
                                {'$set': {'topics': newtopics}})
    return 'ok'


@app.route('/api/conversations/<conv_id>/changeStatus')
def changeStatus(conv_id):
    status = request.args.get('status')
    db.conversations.update_one({'_id': ObjectId(conv_id)}, {'$set' : {'status':status}})
    return "Task Completed"


@app.route('/api/<screen_name>/metrics')
def getMetrics(screen_name):
    open_ones = db.conversations.count({'screen_name':screen_name , 'status':'open'})
    closed_ones = db.conversations.count({'screen_name':screen_name , 'status':'closed'})
    resolved_ones = db.conversations.count({'screen_name':screen_name , 'status':'resolved'})
    return jsonify({
        'open_ones':open_ones,
        'closed_ones':closed_ones+resolved_ones
    })


@app.route('/api/<org_screen_name>/n_issues/<user_screen_name>')
def get_user_issue_count(org_screen_name, user_screen_name):
    response = {
        'count': db.conversations.count({
            'screen_name': org_screen_name,
            'messages.screen_name': user_screen_name
        })
    }
    print(response['count'])
    return jsonify(response)


@app.route('/api/classify', methods=['POST'])
def _classify_it():
    text = request.get_json()['text']
    return jsonify({
        'category': classify(text)
    })
