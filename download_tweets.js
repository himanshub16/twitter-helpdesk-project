const MongoClient = require('mongodb').MongoClient
const assert = require('assert')
const Twit = require('twit')
const env = require('./env')


async function connectToDB(dbUrl, dbName) {
    return (await MongoClient.connect(dbUrl)).db(dbName)
}

async function cursorToArray(cursor) {
    let docs = []
    for (let doc = await cursor.next(); doc != null; doc = await cursor.next()) {
        docs.push(doc)
    }
    return docs
}


async function getWorkToBeDone(db, filename) {
    const data = require(`${__dirname}/${filename}`)
    const tweetsToFind = data.map(each => each.tweet_id)
    let cursor = db.collection('tasks').find({
        name: data[0].name,
    })
    let allThere = await cursorToArray(cursor)
    let completed = allThere.filter(each => each.done)
    let completed_ids = completed.map(each => each.tweet_id)
    let pending = allThere.filter(each => !each.done)
    // let newWork = tweetsToFind.filter(tweet_id => !(tweet_id in completed_ids))
    // in works for prototype chain and jsons.. better use Array.includes
    let newWork = tweetsToFind.filter(tweet_id => !(completed_ids.includes(tweet_id)))

    let idsToInsert = new Set()
    tweetsToFind.forEach(tid => idsToInsert.add(tid))
    allThere.forEach(doc => idsToInsert.delete(doc.tweet_id))

    // let toInsert = Array(...idsToInsert.values().map(tid => {
    //     return {tweet_id: tid, done: false, name: data[0].name}
    // }))
    let toInsert = []
    for (let tid of idsToInsert.values()) {
        toInsert.push({ tweet_id: tid, name: data[0].name, done: false })
    }

    console.log(`
    Calculating work to do:
        Found: ${tweetsToFind.length}
        There: ${allThere.length}
        Completed: ${completed.length}
        Pending: ${pending.length}
        New Work: ${newWork.length}
        To insert: ${toInsert.length}
    `)

    if (toInsert.length) {
        let result = await db.collection('tasks').insertMany(toInsert)
        console.log(`${result.insertedCount} entries inserted of total`)
    }
    return newWork
}


class TaskWorker {
    constructor(workToDo, client, is_parent = false) {
        let d = new Date()
        d.setFullYear(d.getFullYear() + 1)

        this.workToDo = workToDo
        this.taskStatus = {}
        this.client = client
        this.left = 1
        this.nextReset = d.getSeconds() / 1000
        this.results = []
        this.pendingReq = this.workToDo.length
        this.is_parent = is_parent
        if (!is_parent)
            this.parentWorker = new TaskWorker([], client, is_parent = true)

        for (let each of workToDo) {
            this.taskStatus[each] = false
        }
    }

    async save(db) {
        if (this.results.length) {
            let res = await db.collection('tweets').insertMany(this.results)
            console.log('Saving from taskworker', res.nInserted, res.nModified)
        }
    }

    async markDone(db) {
        // let completed = Object.keys(this.taskStatus).filter(twid => this.taskStatus[twid])
        let completed = []
        for (let key of Object.keys(this.taskStatus)) {
            if (this.taskStatus[key])
                completed.push(key)
        }
        let res = await db.collection('tasks').updateMany(
            { tweet_id: { $in: completed } },
            { $set: { done: true } }
        )
        return res
    }

    // async handleResponse(err, data, res) {
    handleResponse(response) {
        // let err = response.err
        // if (err) {
        //     console.error('Error in request')
        //     console.error(err)
        //     return
        // }
        this.results.push(...response.data)
        this.left = Number(response.resp.headers['x-rate-limit-remaining'])
        this.nextReset = Number(response.resp.headers['x-rate-limit-reset'])
    }

    async start(db) {
        let pageSize = 100
        let n_pages = Math.ceil(this.workToDo.length / pageSize)
        // n_pages = 2
        this.pendingReq = n_pages
        let promises = []
        for (let i = 0; i < n_pages; i++) {
            let ids = this.workToDo.slice(i * pageSize, (i + 1) * pageSize)

            let response = await this.client.get('/statuses/lookup', {id: ids, include_entities: true})
        //     // this.client.get('/statuses/lookup', { id: ids, include_entities: true }).then(async (response) => {
        //     promises.push(this.client.get('/statuses/lookup', { id: ids, include_entities: true }))
        // }

        // console.log(`${promises.length} promises pending to be completed. Waiting...`)

        // return Promise.all(promises).then(async (allResponses) => {
        //     // for (let response of allResponses) {
        //     for (let i = 0; i < allResponses.length; i++) {

        //         let response = allResponses[i]
                this.handleResponse(response)
                console.log(`Page ${i}. Found ${response.data.length} items. Pending: ${this.pendingReq - 1}. Results: ${this.results.length} (${this.workToDo.length}). Limit - left : ${this.left}`)

                if (!this.is_parent) {
                    let parentTweetIds = response.data.filter(tweet => tweet.in_reply_to_status_id).map(tweet => tweet.id_str)
                    this.parentWorker.workToDo = parentTweetIds
                    console.log(`Working for parent of page ${i}`)
                    await this.parentWorker.start(db)
                    await this.parentWorker.save(db)
                    this.parentWorker.results = []
                }

                // mark them as done
                response.data.forEach((twid) => { this.taskStatus[twid] = true })
                this.pendingReq -= 1

            }
        // })

    // let interval = setInterval(() => {
    //     if (this.pendingReq === 0) {
    //         oncomplete()
    //         clearInterval(interval)
    //     }
    //     console.log(`waiting for ${this.pendingReq} to complete`)
    // }, 1000)
    }

    // getWorkerForParents() {
    //     let parentTweetIds = this.results.filter(tweet => tweet.in_reply_to_status_id).map(tweet => {
    //         return { tweet_id: tweet.id_str, parent_id: tweet.in_reply_to_status_id }
    //     })

    //     let workerForParents = new TaskWorker(parentTweetIds, this.client)
    //     return workerForParents
    // }
}


async function main() {
    if (process.argv.length < 3) {
        console.error('Missing filename with tweet_ids to grab')
        console.error('Program quits now')
        process.exit(1)
    }

    const db = await connectToDB(env.db_url, env.db_name)

    let workToDo = await getWorkToBeDone(db, process.argv[2])
    // let workToDo = await getWorkToBeDone(db, 'gmail-2017-12-06.json')
    console.log(`There are ${workToDo.length} tasks to be completed`)
    console.log(env.twitter_creds)

    let twClient = new Twit(env.twitter_creds)

    let worker = new TaskWorker(workToDo, twClient)
    // worker.start(async () => {
    //     console.log('completed')
    //     console.log(worker.results.length)
    //     await worker.save(db)

    //     let parentWorker = worker.getWorkerForParents()
    //     parentWorker.start(async () => {
    //         console.log('Parent tweets scraped')
    //         console.log(parentWorker.results.length)
    //         await parentWorker.save()

    //         let res = await worker.markDone(db)
    //         console.log('Marked done. Result is', res)
    //     })
    // })
    await worker.start(db)
    console.log('completed')
    console.log(`Total ${worker.results.length} results found`)
    try {
        await worker.save(db)
    } catch (e) {
        console.error('Some error occurred')
        console.error(e)
    }

    // let parentWorker = worker.getWorkerForParents()
    // await parentWorker.start()
    // console.log(`Total ${parentWorker.results.length} results found`)
    // await parentWorker.save()

    let res = await worker.markDone(db)
    console.log(`Marked done. ${res}`)

    // return worker

    // setTimeout(() => {
    //     console.log(worker.results.length)
    //     console.log(worker.results[0])
    //     // console.log(worker)
    //     // console.log(worker.fetchOriginals())
    //     console.log(worker.pendingReq)
    // }, 5000)
    process.exit(0)
}


// module.exports = {main}
if (typeof require != 'undefined' && require.main == module) {
    main()
}
