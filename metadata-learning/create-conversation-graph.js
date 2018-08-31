const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
const Twit = require('twit');
const env = require('./.env');


var graph = {};

async function connectToDB(dbUrl, dbName) {
    return (await MongoClient.connect(dbUrl)).db(dbName);
}

async function cursorToArray(cursor) {
    let docs = [];
    for (let doc = await cursor.next(); doc != null; doc = await cursor.next()) {
        docs.push(doc);
    }
    return docs;
}


async function prepareGraph(twitter_id, db) {
    console.log('Preparing graph for', twitter_id);
    let allThere = await cursorToArray(
        await db.collection('tweets').find({'user.screen_name': twitter_id,
                                            'in_reply_to_status_id_str': {$ne: null}
                                           }
                                          )
    );

    for (let each of allThere) {
        console.log(each.id_str);
        graph[each.id_str] = [each];
        let taskqueue = [each.in_reply_to_parent_id_str];
        console.log('Working for', parent);
        while (taskqueue.length) {
            db.collection('tweets').findOne(
                {'id_str': parent},
                {},
            );
        }
    }
}


async function main() {
    const twitter_id = process.argv[2];

    var db = await connectToDB(env.mongodb, env.database);
    await prepareGraph(twitter_id, db);

    console.log(Object.keys(graph).length);

    process.exit(0);
}


if (typeof require != 'undefined' && require.main == module) {
    main();
}
