#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from time import sleep, time
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
import json
import datetime
import logging
import sys


def is_python_3_5():
    return (sys.version_info.major is 3) and (sys.version_info.minor is 5)

def is_python_3_6():
    return (sys.version_info.major is 3) and (sys.version_info.minor is 6)


format_ts = lambda dt: dt.strftime('%Y-%m-%d')
logging.basicConfig(format='%(asctime)s %(process)d %(message)s', datefmt='%I:%M:%S %p', level=logging.INFO, filename='log.txt')


def get_firefox_driver():
    # return webdriver.Remote(
    #     desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)
    return webdriver.Firefox(
        firefox_binary='/usr/bin/firefox-developer-edition'
    )
    # return webdriver.Chrome(
    #     executable_path='/usr/lib/chromium-browser/chromedriver'
    # )


def new_tweet_from_selenium_div(div):
    gattr = lambda key: div.get_attribute('data-' + '-'.join(key.split('_')))

    timestamp = div.find_element_by_css_selector(
        '.time a.tweet-timestamp span._timestamp'
    ).get_attribute('data-time')

    data_attrs_of_concern = [
        'tweet_id', 'item_id', 'permalink_path', 'conversation_id',
        'is_reply_to', 'has_parent_tweet', 'tweet_nonce', 'user_id',
        'screen_name', 'name', 'mentions', 'reply_to_users_json'
    ]
    tweet = {
        key: gattr(key)
        for key in data_attrs_of_concern
    }
    tweet['timestamp'] = timestamp
    tweet['reply_to_users_json'] = json.loads(tweet['reply_to_users_json'])
    return tweet


class TweetScraper(object):
    _tweet_selector = 'li.js-stream-item > div.js-stream-tweet'
    _wait_time = 1

    def __init__(self, screen_name, start_date, end_date, driver=None):
        self.screen_name = screen_name
        self.start_date = start_date
        self.end_date = end_date
        self.tweets = []
        self.driver = get_firefox_driver() if driver is None else driver
        self.counts = {}
        # self.driver = get_firefox_driver()

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.tweets))

        # print('saved', len(self.tweets), 'tweets', 'at', filename)
        logging.info(':: %s :: Saved %d tweets to %s', self.screen_name, len(self.tweets), filename)


    def update_stats(self):
        filename = '{}-stats.json'.format(self.screen_name)
        try:
            with open(filename) as f:
                if is_python_3_5:
                    content = f.read().trim()
                else:
                    content = f.read().strip()
            stats = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            stats = {}

        for key, value in self.counts.items():
            stats[key] = value

        with open(filename, 'w') as f:
            f.write(json.dumps(stats))

        # print('updated stats')
        logging.info(':: %s :: Updated stats', self.screen_name)


    def get_search_url(self, begin, end):
        return 'https://twitter.com/search?l=&q=from%3A{}%20since%3A{}%20until%3A{}&src=typd'.format(
            self.screen_name, format_ts(begin), format_ts(end)
        )

    def get_date_range(self):
        n_days = (self.end_date - self.start_date).days + 1
        for day in range(n_days):
            yield (self.end_date + datetime.timedelta(days=-day-1),
                   self.end_date + datetime.timedelta(days=-day))


    def start_scraping(self, n_tweet_cap=0):
        # timer = time()
        # elapsed = lambda : '{} {} ::'.format(self.screen_name, int(time()-timer))
        date_so_far = self.start_date
        # temp_filename = f'.{self.screen_name}-{int(time())}.cache.json'
        temp_filename = '.{}-{}.cache.json'.format(self.screen_name, int(time()))
        for begin, end in self.get_date_range():
            if n_tweet_cap and len(self.tweets) > n_tweet_cap:
                break

            date_so_far = begin
            url = self.get_search_url(begin, end)
            # print(begin, 'to', end, 'looking up at', url)
            logging.info(':: %s :: Looking up at %s', self.screen_name, url)

            trying = 5
            while trying:
                try:
                    self.driver.get(url)
                    trying = 0
                except TimeoutException:
                    trying -= 1
                    pass
            sleep(self._wait_time)

            try:
                found_tweets = self.driver.find_elements_by_css_selector(self._tweet_selector)
                n_found = 0
                while len(found_tweets) > n_found:
                    # scroll to bottom
                    # print(elapsed(), 'scrolling down. found', len(found_tweets), 'n_found =', n_found)
                    logging.info(':: %s :: Scrolling down. Found %d  |  Total %d  |  n_found %d',
                                 self.screen_name, len(found_tweets), len(self.tweets), n_found)
                    self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(self._wait_time)
                    n_found = len(found_tweets)
                    found_tweets = self.driver.find_elements_by_css_selector(self._tweet_selector)
                    # n_found += 10   # ensure enough scrolls

                self.counts[format_ts(date_so_far)] = len(found_tweets)

                for tweet_elem in found_tweets:
                    try:
                        tweet = new_tweet_from_selenium_div(tweet_elem)
                        self.tweets.append(tweet)
                    except StaleElementReferenceException as exc:
                        # print('lost element reference', exc)
                        logging.error('lost element reference %s', exc)

                self.save(temp_filename)
                # print(elapsed(), 'total tweets here', len(self.tweets))
                logging.info(':: %s :: ', self.screen_name)

            except NoSuchElementException as exc:
                # print(elapsed(), 'not tweets on this day')
                logging.error(':: %s :: No tweets on this day', self.screen_name)

        self.driver.close()
        self.update_stats()
        return date_so_far


def do_it_for_one(screen_name, start, end, n_tweet_cap=0):
    engine = TweetScraper(screen_name, start, end)
    date_so_far = engine.start_scraping(n_tweet_cap)
    filename = '{}-{}.json'.format(screen_name, format_ts(date_so_far))
    print(filename, 'for', screen_name)
    engine.save(filename)
    logging.info(':: %s :: final save at %s', screen_name, filename)
    # print('date saved to file', filename)
    print(engine.counts)


def main():
    start = datetime.datetime.now() + datetime.timedelta(days=-6*30)
    end = datetime.datetime.now()
    n_tweet_cap = 10000
    # screen_names = ['ola_supports', 'RailMinIndia', 'UberINSupport', 'flipkartsupport', 'PMOIndia', 'DoT_India']
    # screen_names = ['RailMinIndia', 'ola_supports']
    # screen_names = screen_names[:1]
    import sys
    do_it_for_one(sys.argv[1], start, end, n_tweet_cap)

    # import concurrent.futures
    # with ProcessPoolExecutor() as executor:
    # with ThreadPoolExecutor() as executor:
        # futures = [
        #     executor.submit(do_it_for_one, each, start, end, n_tweet_cap)
        #     for each in screen_names
        # ]

        # for fut in as_completed(futures):
        #     print(fut.result())
        # args = [(name, start, end, n_tweet_cap) for name in screen_names]
        # print('dealing for',args)
        # for _ in zip(args, executor.map(do_it_for_one, args)):
        #     print('done for', args[0])

    # engine = TweetScraper('ola_supports', start, end)
    # date_so_far = engine.start_scraping(n_tweet_cap=10000)
    # filename = 'ola_supports-{}.json'.format(format_ts(date_so_far))
    # engine.save(filename)
    # print('date saved to file', filename)
    # print(engine.counts)


if __name__=='__main__':
    main()
