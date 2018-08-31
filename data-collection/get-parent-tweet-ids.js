const cursorToArray = require('./download_tweets').cursorToArray
const connectToDB = require('./download_tweets').connectToDB
const env = require('./env')
const fs = require('fs')


async function getParentTasks(db, screen_name) {
    let cursor = db.collection('tweets').find(
        {
            in_reply_to_user_id_str: {
                $ne: null
            },
            "user.screen_name": {
                $eq: screen_name
            },
        },
        {
            in_reply_to_user_id_str: true,
            "user.screen_name": true,
            _id: false
        }
    )

    let allThere = await cursorToArray(cursor)
    let prepared = allThere.map(
        entry => {
            return {
                tweet_id: entry.in_reply_to_user_id_str,
                name: entry.user.screen_name
            }
        }
    )

    // pagination is not required
    return prepared

    // let total = prepared.length
    // const page_size = 800
    // let n_pages = total / page_size
    // let pages = []

    // for (let i = 0; i <= n_pages; i++) {
    //     pages.push(prepared.slice(
    //         i*page_size,
    //         (i+1)*page_size
    //     ))
    // }

    // return pages
}


// function save_task_group(tasks, screen_name, group_id) {
//     fs.writeFileSync(`./tasks/${screen_name}-${group_id}.json`, JSON.stringify(tasks))
//     console.log('Saving', tasks.length, 'tasks at', `./tasks/${screen_name}-${group_id}.json`)
// }

function save_task(tasks, screen_name) {
        fs.writeFileSync(`./tasks/${screen_name}.json`, JSON.stringify(tasks))
        console.log('Saving', tasks.length, 'tasks at', `./tasks/${screen_name}.json`)
}


async function main() {
    const db = await connectToDB(env.db_url, env.db_name)
    console.log('connected successfully')

    // let screen_name = 'gmail'
    let screen_name = process.argv[2]
    save_task(await getParentTasks(db, screen_name), screen_name)
    // let i = 0
    // for (let each of await getParentTasks(db, screen_name)) {
    //     save_task_group(each, screen_name, i)
    //     // console.log(each.length)
    //     i++
    // }
    process.exit(0)
}

// module.exports = {main}
if (typeof require != 'undefined' && require.main == module) {
    main()
}
