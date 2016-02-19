#!/usr/bin/env python
# -*- coding: utf-8 -*-
import twitter
import urlparse
from pprint import pprint as pp
import logging
from iojson import IO_json
from iocsv import IO_csv
from iomongo import IO_mongo
import time
import sys, os
CONSUMER_KEY    =   'FwhiUUCVZ7EAIciYi2nwfXn1h'
CONSUMER_SECRET =   'yFoTb2hrezDLdGDzM0Ks4UdfKKdBCFB1Zb6i9l9Fl4Hb8XWm5D'
OAUTH_TOKEN =   '1679287802-FJtYQSM4IEEXrTHsbN81VWrOSBMPhftEkQUxauA'
OAUTH_TOKEN_SECRET  =   'cwsFFttz0PfMR8ZBPvUoQfG8OKJ8kPYGwMeXXtcWgbsor'

class TwitterApi(object):
    """
    TwitterAPI	class	allows	the	Connection	to	Twitter	via	OAuth
    once	you	have	registered	with	Twitter	and	receive	the	
    necessary	credentiials
    """

    def __init__(self):
        consumer_key = CONSUMER_KEY #'Provide your credentials'
        consumer_secret = CONSUMER_SECRET #'Provide your credentials'
        access_token    = OAUTH_TOKEN #'Provide your credentials'
        access_secret   = OAUTH_TOKEN_SECRET #'Provide your credentials'

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.auth = twitter.oauth.OAuth(access_token,access_secret, consumer_key,consumer_secret)
        self.api = twitter.Twitter(auth=self.auth)
        self.retries = 3
        self.logger = logging.getLogger(TwitterApi.__name__)
        if not os.path.isdir('log'):
            os.mkdir('log')
            os.mknod('log/log.txt')
        fileHandler = logging.FileHandler(
            "{0}/{1}.log".format(os.path.join(os.getcwd(),'log'),'file'))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler) 
        self.logger.setLevel(logging.DEBUG)
        if not os.path.isdir('data'):
            os.mkdir('data/json')
            os.mkdir('data/csv')
        self.jsonSaver = IO_json(os.path.join(
            os.getcwd(),'data/json'), 'result')
        self.csvSaver = IO_csv(os.path.join(
            os.getcwd(),'data/csv'), 'result')
        self.mongoSaver = IO_mongo(db='twtr01_db', coll='twtr01_coll')

    def searchTwitter(self, q, max_res=10,**kwargs):
        max_results = min(1000,max_res)
        search_results = self.api.search.tweets(q=q, count=max_results, **kwargs)
        statuses = search_results['statuses']
        for _ in range(max_results):
            try:
                next_results = search_results['search_metadata']['next_results']
            except KeyError as e:
                self.logger.error('error in searchTwitter: %s',e)
                break
            next_results = urlparse.parse_qsl(next_results[1:])
            kwargs = dict(next_results)
            search_results  = self.api.search.tweets(**kwargs)
            statuses += search_results['statuses']
            #self.saveTweets(search_results['statuses'])
            if len(statuses) > max_results:
                self.logger.info('info in searchTwitter - got %i \
                    tweets - max: %i' %(len(statuses),max_results))
                break
        return statuses

    def parseTweets(self, statuses):
        return [ (status['id'],
            status['created_at'],
            status['user']['id'],
            status['user']['name'],
            status['text'], url['expanded_url'])
            for status  in  statuses
            for url in  status['entities']['urls']
        ]

    def saveTweetsWithMongo(self,statuses):
        for s in statuses:
            self.mongoSaver.save(s)
            
    def saveTweetsWithCSV(self,statuses):
        self.csvSaver.save(statuses)
        
    def saveTweetsWithJSON(self,statuses):
        self.jsonSaver.save(statuses)  
        
    def getTweets(self, q, max_res=10):
        def handleError(e, wait_period=2, sleep_when_rate_limited=True):
            if wait_period > 3600:
                self.logger.error('Too many retries in getTweets:  %s', e)
                raise e
            if e.e.code == 401:
                self.logger.error('error 401 * Not Authorised * in getTweets: %s', e)
                return  None
            elif e.e.code == 404:
                self.logger.error('error 404 * Not Authorised * in getTweets: %s', e)
                return  None
            elif e.e.code == 429:
                self.logger.error('error 429 * API Rate Limit Exceeded * in  getTweets:  %s', e)
                if sleep_when_rate_limited:
                    self.logger.error('error 429 * Retrying in  15  minutes * in  getTweets:  %s', e)
                    sys.stderr.flush()
                    time.sleep(60*15 + 5)
                    self.logger.info('error 429 * Retrying now * in  getTweets:  %s', e)
                    return 2
                else:
                    raise e
            elif e.e.code in (500, 502, 503, 504):
                self.logger.info('Encountered %i  Error.  Retrying in  %i seconds' % (e.e.code,  wait_period))
                time.sleep(wait_period)
                wait_period *=  1.5
                return  wait_period
            else:
                self.logger.error('Exit - aborting - %s', e)
                raise e

        while True:
            try:
                self.searchTwitter(q, max_res=10)
            except twitter.api.TwitterHTTPError as e:
                error_count = 0   
                wait_period = handleError(e, wait_period)
                if wait_period is None:
                    return




