# GUI and others
# from calendar import c
# from matplotlib.pyplot import get
# import pandas as pd

# stock data gathering,plotting and prediction
# import datetime
# import yfinance as yf
# from plotly import graph_objs as go

#webscrapping
# from urllib.request import urlopen, Request
# from bs4 import BeautifulSoup
# import requests

# twitter library and internal files
import tweepy
import config
import bert_model

#  API v1 Auth
auth = tweepy.OAuth1UserHandler(
    config.TWITTER_COMSUMER_KEY,
    config.TWITTER_COMSUMER_SECRET,
    config.TWITTER_ACCESS_TOKEN,
    config.TWITTER_ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# API v2 Auth
client = tweepy.Client( bearer_token = config.BEARER_TOKEN)

# Twitter
def tweet_analysis(link):

    tweet_id = link[(link.rfind('/'))+1:]
    
    # FUNCTIONS
    def get_replies(tweet_id):
        if tweet_id:
            limit = 20
            reply_objs = []
            my_query = 'conversation_id:' + tweet_id + ' lang:en'
            # my_exp = ['geo.place_id','author_id']
            
            # v2 used
            tweets_list = client.search_recent_tweets(query = my_query, max_results = limit)
            status_list = tweets_list[0]

            # tweets_list
            # status_list

            for status_response in status_list:
                if not status_response:
                    print("[INFO] Status response empty")
                    continue

                # status_id
                # print(status_response.data)

                status_id = status_response['data']['id']
                print(status_id)

                # v1 used
                status = api.get_status(status_id)
                data = get_tweet_data(status)
                reply_objs.append(data)

            return reply_objs


    def get_tweet_data(status):
        lang = status.lang
        if lang!="en":  return

        # INFO
        data = dict()
        data['text'] = status.text
        data['location'] = status.user.location
        data['created_at'] = status.created_at.strftime("%m-%d-%Y  %I:%M:%S %p")
        data['favorite_count'] = status.favorite_count
        data['retweet_count'] = status.retweet_count
        # data['possibly_sensitive'] = status.possibly_sensitive
        # data['withheld_in_countries'] = status.withheld_in_countries
        return data

    def get_avg_user_info(user):
        len=0
        data = {'favorite_count':0,'retweet_count':0,'sentiment_score':0,'variance_score':0}
        comments_data = list()

        # v1 used
        tweets = api.user_timeline(screen_name=user.screen_name)
        for status in tweets:
            len+=1

            # individual data
            individual_com_data = dict()
            individual_com_data['text'] = status.text
            individual_com_data['created_at'] = status.created_at.strftime("%m-%d-%Y  %I:%M:%S %p")
            individual_com_data['favorite_count'] = status.favorite_count
            individual_com_data['retweet_count'] = status.retweet_count

            sentiment_score,variance_score = bert_model.get_individual_sentiment_score(status.text)
            individual_com_data['sentiment_score'] = sentiment_score
            individual_com_data['variance_score'] = variance_score
            comments_data.append(individual_com_data)

            # avg data
            data['sentiment_score'] += sentiment_score
            data['variance_score'] += variance_score
            data['favorite_count'] += status.favorite_count
            data['retweet_count'] += status.retweet_count
        
        data['sentiment_score'] /= len
        data['variance_score'] /= len
        data['favorite_count'] /= len
        data['retweet_count'] /= len


        return data,comments_data


    # MAIN FLOW START
    if tweet_id:
        # v1 used
        status = api.get_status(tweet_id)

        # RADAR CHART

        # FOR CURRENT USER TWEET
        user = status.user
        # normal data
        cur_data = get_tweet_data(status)
        # scores
        cur_sentiment_score, cur_variance_score = bert_model.get_individual_sentiment_score(status.text)
        cur_comment_data = [cur_data, cur_sentiment_score, cur_variance_score]

        # AVERAGE for user timeline
        # normal data and scores
        avg_data_info, comments_data = get_avg_user_info(user)
        print("avg_data_info")
        print(avg_data_info)
        print("comments_data")
        print(comments_data)

        # for replies
        reply_objs = get_replies(tweet_id)

        # SENTIMENT ANALYSIS 
        if reply_objs:

            total_avg_result, world_map_avg_score, locations = bert_model.get_map_sentiment_score(reply_objs)
            print("total_avg_result")
            print(total_avg_result)

            print("world_map_avg_score")
            print(world_map_avg_score)

            return total_avg_result,world_map_avg_score, cur_comment_data, avg_data_info, comments_data  
        else:

            print('Reply_objs list empty!')
            return [-1],[-1],[-1],[-1],[-1]
