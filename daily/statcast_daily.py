#!/usr/bin/env python
# coding: utf-8

# # Import Libraries

from pybaseball import *
from daily_functions import *
import pandas as pd
import numpy as np
import math
import os
import shutil
import time
from datetime import date
from datetime import timedelta
import tweepy
from pandas.io.json import json_normalize
import requests
import statcast_secrets


# # Import Data

# import player data
player_data = chadwick_register()
# remove old players to decrease size
player_data = player_data[player_data.mlb_played_last>1990]

# find yesterday's date
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# download statcast data
data = statcast(start_dt=yesterday)


# # Clean Data and Save File

# run function to add player names & teams
df = clean_data(data, player_data)

# save data in file system
yesterday_file = f"{yesterday}.csv"
df.to_csv(os.path.join('C:\\', 'Users', 'Owner', 'Documents', 'Moneyball', 'statcast',
                       'daily', 'daily_data_v2', yesterday_file))


# # Run Daily Functions

# homer distances
homer_distance_high = homer_distance(df)
homer_distance_low = homer_distance(df, bottom=True)
# pitch speeds
pitch_speed_high = pitch_speed(df)
pitch_speed_low = pitch_speed(df, bottom=True)
# launch speeds
launch_speed_high = launch_speed(df, only_events=True)
launch_speed_low = launch_speed(df, bottom=True, only_events=True)
# long plate appearances
pitches_seen_atbat_high = pitches_seen(df, atbat=True)
# win prob changes
win_prob_high = win_prob(df)


# # Create Tweets

socials = {
    'BAL': {'at':'@Orioles',      'hashtag':'#Birdland'},
    'BOS': {'at':'@RedSox',       'hashtag':'#DirtyWater'},
    'NYY': {'at':'@Yankees',      'hashtag':'#RepBX'},
    'TB':  {'at':'@RaysBaseball', 'hashtag':'#RaysUp'},
    'TOR': {'at':'@BlueJays',     'hashtag':'#NextLevel'},
    'CWS': {'at':'@whitesox',     'hashtag':'#ChangeTheGame'},
    'CLE': {'at':'@CleGuardians', 'hashtag':'#ForTheLand'},
    'DET': {'at':'@tigers',       'hashtag':'#DetroitRoots'},
    'KC':  {'at':'@Royals',       'hashtag':'#TogetherRoyal'},
    'MIN': {'at':'@Twins',        'hashtag':'#MNTwins'},
    'HOU': {'at':'@astros',       'hashtag':'#LevelUp'},
    'LAA': {'at':'@Angels',       'hashtag':'#GoHalos'},
    'OAK': {'at':'@Athletics',    'hashtag':'#DrumTogether'},
    'SEA': {'at':'@Mariners',     'hashtag':'#SeaUsRise'},
    'TEX': {'at':'@Rangers',      'hashtag':'#StraightUpTX'},
    'ATL': {'at':'@Braves',       'hashtag':'#ForTheA'},
    'MIA': {'at':'@Marlins',      'hashtag':'#MakeItMiami'},
    'NYM': {'at':'@Mets',         'hashtag':'#LGM'},
    'PHI': {'at':'@Phillies',     'hashtag':'#RingTheBell'},
    'WSH': {'at':'@Nationals',    'hashtag':'#Natitude'},
    'CHC': {'at':'@Cubs',         'hashtag':'#ItsDifferentHere'},
    'CIN': {'at':'@Reds',         'hashtag':'#ATOBTTR'},
    'MIL': {'at':'@Brewers',      'hashtag':'#ThisIsMyCrew'},
    'PIT': {'at':'@Pirates',      'hashtag':'#LetsGoBucs'},
    'STL': {'at':'@Cardinals',    'hashtag':'#STLCards'},
    'ARI': {'at':'@Dbacks',       'hashtag':'#Dbacks'},
    'COL': {'at':'@Rockies',      'hashtag':'#Rockies'},
    'LAD': {'at':'@Dodgers',      'hashtag':'#AlwaysLA'},
    'SD':  {'at':'@Padres',       'hashtag':'#TimeToShine'},
    'SF':  {'at':'@SFGiants',     'hashtag':'#SFGameUp'}
}


# Create Tweets

# homer tweets
homer_high_tweet = create_homer_high_tweet(homer_distance_high, socials)
homer_low_tweet = create_homer_low_tweet(homer_distance_low, socials)

# pitch tweets
pitch_high_tweet = create_pitch_high_tweet(pitch_speed_high, socials)
pitch_low_tweet = create_pitch_low_tweet(pitch_speed_low, socials)

# exit velocity tweets
ev_high_tweet = create_ev_high_tweet(launch_speed_high, socials)
ev_low_tweet = create_ev_low_tweet(launch_speed_low, socials)

# long PA tweet
atbat_long_tweet = create_atbat_long_tweet(pitches_seen_atbat_high, socials)

# win prob tweet
win_prob_tweet = create_win_prob_tweet(win_prob_high, socials)

# put tweets into list
tweets = [homer_high_tweet, homer_low_tweet, pitch_high_tweet, pitch_low_tweet,
          ev_high_tweet, ev_low_tweet, atbat_long_tweet, win_prob_tweet]


# Preview Tweets

for tweet in tweets:
    print(tweet)
    print('\n')


# # Publish Tweets

# Create Twitter Client

client = tweepy.Client(
    bearer_token=statcast_secrets.bearer_token, 
    consumer_key=statcast_secrets.api_key, 
    consumer_secret=statcast_secrets.api_key_secret, 
    access_token=statcast_secrets.access_token, 
    access_token_secret=statcast_secrets.access_token_secret, 
    return_type = requests.Response,
    wait_on_rate_limit=True
)


# Send Tweets

for tweet in tweets:
    try:
        client.create_tweet(text=tweet)
    except:
        client.create_tweet(text=tweet[:270])



