# import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from statistics import variance,mean
import time
from geopy.geocoders import Nominatim
import spacy

# frequently used models
nlp = spacy.load('en_core_web_sm')
geolocator = Nominatim(user_agent = "geoapiExercises")

print('[INFO] BERT model loaded!')
print('[INFO] Iterating on replies!')
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

def check_location(text):

    # word_list = text.split(' ').reverse()
    # words = nlp(word_list)
    words = nlp(text)
    for word in words.ents:
        if word.label_ == 'GPE':
            word_text = word.text
            location = geolocator.geocode(word_text)
            print(f'location : {location}')
            # try returning the longitudes and the latitudes
            # return str(location)
            return word_text
    
    return ""

def get_individual_sentiment_score(text):
    # textual analysis
    tokens = tokenizer.encode(text, return_tensors='pt') # type of tensors = pytorch
    result = model(tokens) # result has column logits
    values = [val.item() for val in result.logits[0]]

    sentiment_score = int(torch.argmax(result.logits))+1
    variance_score = round(variance(values),2)

    return sentiment_score,variance_score


def get_map_sentiment_score(reply_objs):
    start_time = time.time()

    locations = []
    variance_list = []
    sentiment_list = []
    world_map_score = dict()

    rl = len(reply_objs)
    print(f'[INFO] list length =  {rl}')

    for reply in reply_objs:

        # textual analysis
        text = reply['text']
        tokens = tokenizer.encode(text, return_tensors='pt') # type of tensors = pytorch
        result = model(tokens) # result has column logits
        values = [val.item() for val in result.logits[0]]

        sentiment_score = int(torch.argmax(result.logits))+1
        variance_score = round(variance(values),2)

        # factoring in other parameters
        sentiment_score = sentiment_score + (reply['retweet_count']/100)
        sentiment_score = sentiment_score + (reply['favorite_count']/100)

        sentiment_list.append(sentiment_score)
        variance_list.append(variance_score)

        loc = check_location(reply['location'])

        if loc!='' and loc!='None' and loc!='none':
            # print(f"rough loc = {reply['location']}")
            reply['location'] = loc
            # print(f"eval loc = {reply['location']}")

            locations.append(reply['location'])

            if reply['location'] not in world_map_score.keys():
                world_map_score[reply['location']] = dict()

            if 'Sentiment_list' not in world_map_score[reply['location']].keys() : 
                world_map_score[reply['location']]['sentiment_list'] = []

            if 'variance_list' not in world_map_score[reply['location']].keys() : 
                world_map_score[reply['location']]['variance_list'] = []

            world_map_score[reply['location']]['sentiment_list'].append(sentiment_score)
            world_map_score[reply['location']]['variance_list'].append(variance_score)
    
    total_avg_result = []
    total_avg_result.append(round(mean(sentiment_list),2))
    total_avg_result.append(round(mean(variance_list),2))

    world_map_avg_score = dict()
    
    for loc in locations:
        if loc!='' and loc!='None' and loc!='none':

            if loc not in world_map_avg_score.keys():
                world_map_avg_score[loc] = dict()

            if 'sentiment_list' not in world_map_avg_score[loc].keys():
                world_map_avg_score[loc]['sentiment_list'] = 0
                
            if 'variance_list' not in world_map_avg_score[loc].keys():
                world_map_avg_score[loc]['variance_list'] = 0

            world_map_avg_score[loc]['sentiment_list'] = round(mean(world_map_score[loc]['sentiment_list']),2)
            world_map_avg_score[loc]['variance_list'] = round(mean(world_map_score[loc]['variance_list']),2)

    print("--- %s seconds ---" % (time.time() - start_time))

    return total_avg_result, world_map_avg_score, locations
