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
from PIL import Image, ImageDraw, ImageFont
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

# homer distance
homer_distance_high = homer_distance(df)
# pitch speed
pitch_speed_high = pitch_speed(df)
# launch speed
launch_speed_high = launch_speed(df, only_events=True)
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

suffix_dict = {
    1:'st',
    2:'nd',
    3:'rd',
    4:'th',
    5:'th',
    6:'th',
    7:'th',
    8:'th',
    9:'th',
    10:'th',
    11:'th',
    12:'th',
    13:'th',
    14:'th',
    15:'th',
    16:'th',
    17:'th',
    18:'th'
}

series_dict = {
    
    'PHI':['WS', 'GAME6'],
    'HOU':['WS', 'GAME6'],
    
    'SD': ['NLCS', 'GAME5'],
    'NYY':['ALCS', 'GAME4'], 
    'CLE':['ALDS', 'GAME5'],
    'LAD':['NLDS', 'GAME4'],
    'ATL':['NLDS', 'GAME4'],
    'SEA':['ALDS', 'GAME3'],
    'NYM':['NLWC', 'GAME3'],
    'STL':['NLWC', 'GAME2'],
    'TB': ['ALWC', 'GAME2'],
    'TOR':['ALWC', 'GAME2'],
    'BOS':['NONE', 'GAME1'],
    'BAL':['NONE', 'GAME1'],
    'CWS':['NONE', 'GAME1'],
    'MIN':['NONE', 'GAME1'],
    'DET':['NONE', 'GAME1'],
    'KC': ['NONE', 'GAME1'],
    'LAA':['NONE', 'GAME1'],
    'OAK':['NONE', 'GAME1'],
    'TEX':['NONE', 'GAME1'],
    'MIA':['NONE', 'GAME1'],
    'WSH':['NONE', 'GAME1'],
    'MIL':['NONE', 'GAME1'],
    'CHC':['NONE', 'GAME1'],
    'PIT':['NONE', 'GAME1'],
    'CIN':['NONE', 'GAME1'],
    'SF': ['NONE', 'GAME1'],
    'ARI':['NONE', 'GAME1'],
    'COL':['NONE', 'GAME1']
}

team_names_dict = {
    'NYY':'Yankees',
    'TOR':'Blue Jays',
    'TB':'Rays',
    'BOS':'Red Sox',
    'BAL':'Orioles',
    'CLE':'Guardians',
    'CWS':'White Sox',
    'MIN':'Twins',
    'DET':'Tigers',
    'KC':'Royals',
    'HOU':'Astros',
    'SEA':'Mariners',
    'LAA':'Angels',
    'OAK':'Athletics',
    'TEX':'Rangers',
    'NYM':'Mets',
    'ATL':'Braves',
    'PHI':'Phillies',
    'MIA':'Marlins',
    'WSH':'Nationals',
    'STL':'Cardinals',
    'MIL':'Brewers',
    'CHC':'Cubs',
    'PIT':'Pirates',
    'CIN':'Reds',
    'LAD':'Dodgers',
    'SD':'Padres',
    'SF':'Giants',
    'ARI':'DBacks',
    'COL':'Rockies'
}


# # Revamped win_prob Function

def win_prob_v2(df, n=5, all_data=False, extra=False):
    """This function returns the largest changes in win percentage of the day.
    
    n controls how many results are returned.
    all_data returns every result, but sorted.
    """
    
    win_prob = df.copy(deep=True)
    win_prob = win_prob[~win_prob['events'].isna()]
    
    win_prob['home_win_pct_abs'] = abs(win_prob['delta_home_win_exp'])*100
    win_prob['home_win_pct'] = win_prob['delta_home_win_exp']*100
    win_prob = win_prob.sort_values(by='home_win_pct_abs', ascending=False)
    win_prob['batter_home'] = win_prob['batter_team']==win_prob['home_team']
    win_prob['batter_win_pct'] = np.where(win_prob['batter_home'], round(win_prob['home_win_pct'],1), -1*round(win_prob['home_win_pct'],1))
    win_prob['batter_win_+-'] = np.where(win_prob['batter_win_pct']>0, "+", "")
    win_prob['batter_win_pct_str'] = win_prob['batter_win_+-'] + win_prob['batter_win_pct'].astype(str)
    
    if not extra:
        win_prob = win_prob[['batter_name', 'batter_team', 'home_team', 'batter_home', 'home_win_pct',
                   'batter_win_pct_str', 'events', 'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type', 'game_date']]
    
    win_prob = win_prob.iloc[:n]
    
    return win_prob


# # Creating Tweet Text

def win_prob_by_game(df):
    
    game_tweets = list()
    
    game_IDs = list(df.game_pk.unique())
    for game in game_IDs:
        game_df = df[df.game_pk==game]
        game_wp = win_prob_v2(game_df)
        
        away_team = game_df.away_team.iloc[0]
        home_team = game_df.home_team.iloc[0]
        series = series_dict[home_team]
        
        game_tweets.append(create_game_win_prob_tweet(game_wp, away_team, home_team, series, socials))
    
    return game_tweets
    
    for tweet in game_tweets:
        print(tweet)
        print('\n\n')


def create_game_win_prob_tweet(win_prob_high, away_team, home_team, series, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = win_prob_high.iloc[i,0]
        team = win_prob_high.iloc[i,1]
        try:
            event = win_prob_high.iloc[i,2].replace('_', ' ')
        except:
            continue
            
        prob = win_prob_high.iloc[i,3]
        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {prob}% ({event})\n    {socials[team]['hashtag']}\n"

        strings.append(string)

    # text = '\n'.join(strings)
    # text = f"{away_team} @ {home_team} ({series})\nLargest Changes in Win Probability 📈\n({date_str})\n\n" + text
    
    text = f"{series[0]} {series[1][:-1].title()} {series[1][-1]} - ({date_str})\n{team_names_dict[away_team]} @ {team_names_dict[home_team]}\n\n{socials[away_team]['hashtag']}\n{socials[home_team]['hashtag']}\n#Postseason"
    img_file = f"{date_str}_{home_team}-{away_team}.png".replace('/', '-')

    return [text, img_file]


tweets = win_prob_by_game(df)   # [text, img_file]


# # Creating Graphics

def get_winner(df):
    
    # figure out winner
    home = df.post_home_score.max()
    away = df.post_away_score.max()
    if home>away:
        winner = team_names_dict[df.home_team.iloc[0]]
    else:
        winner = team_names_dict[df.away_team.iloc[0]]
        
    # create text
    return (winner, home, away)


def get_series_game(game_wp):
    
    series = series_dict[game_wp.home_team.iloc[0]][0]
    game_num = series_dict[game_wp.home_team.iloc[0]][1]
    return (series, game_num)


def get_score_change(game_wp, row):
    
    pre_bat = str(game_wp.home_score.iloc[row])
    if len(pre_bat)==1:
        pre_bat = "0"+pre_bat
    pre_bat1 = pre_bat[0]
    pre_bat2 = pre_bat[1]
        
    pre_fld = str(game_wp.away_score.iloc[row])
    if len(pre_fld)==1:
        pre_fld = "0"+pre_fld
    pre_fld1 = pre_fld[0]
    pre_fld2 = pre_fld[1]
        
    post_bat = str(game_wp.post_home_score.iloc[row])
    if len(post_bat)==1:
        post_bat = "0"+post_bat
    post_bat1 = post_bat[0]
    post_bat2 = post_bat[1]
        
    post_fld = str(game_wp.post_away_score.iloc[row])
    if len(post_fld)==1:
        post_fld = "0"+post_fld
    post_fld1 = post_fld[0]
    post_fld2 = post_fld[1]
    
    # text = f"{pre_bat}-{pre_fld}»{post_bat}-{post_fld}"
    
    return (pre_bat1, pre_bat2, pre_fld1, pre_fld2, post_bat1, post_bat2, post_fld1, post_fld2)


def win_prob_graphics(df):
    
    game_IDs = list(df.game_pk.unique())
    for game in game_IDs:
        game_df = df[df.game_pk==game]
        winner, home_final, away_final = get_winner(game_df)
        game_wp = win_prob_v2(game_df, extra=True)
        away_team = game_df.away_team.iloc[0]
        home_team = game_df.home_team.iloc[0]
        series, game_num = get_series_game(game_wp)
        
        create_graphic(game_wp, away_team, home_team, winner, home_final, away_final, series, game_num)


def create_graphic(game_wp, away_team, home_team, winner, home_final, away_final, series, game_num):
    
    #TODO extract info from game_wp df
    player_1 = game_wp['batter_name'].iloc[0]
    player_2 = game_wp['batter_name'].iloc[1]
    player_3 = game_wp['batter_name'].iloc[2]
    event_1 = game_wp['events'].iloc[0].replace('_', ' ').title().replace('Grounded Into ','').upper().replace('FIELDERS CHOICE', 'FC').replace('HIT BY PITCH', 'HBP').replace('STRIKEOUT DOUBLE PLAY', 'DOUBLE PLAY').title().replace('Hbp', 'HBP')
    event_2 = game_wp['events'].iloc[1].replace('_', ' ').title().replace('Grounded Into ','').upper().replace('FIELDERS CHOICE', 'FC').replace('HIT BY PITCH', 'HBP').replace('STRIKEOUT DOUBLE PLAY', 'DOUBLE PLAY').title().replace('Hbp', 'HBP')
    event_3 = game_wp['events'].iloc[2].replace('_', ' ').title().replace('Grounded Into ','').upper().replace('FIELDERS CHOICE', 'FC').replace('HIT BY PITCH', 'HBP').replace('STRIKEOUT DOUBLE PLAY', 'DOUBLE PLAY').title().replace('Hbp', 'HBP')
    pct_1 = game_wp['batter_win_pct_str'].iloc[0]
    pct_2 = game_wp['batter_win_pct_str'].iloc[1]
    pct_3 = game_wp['batter_win_pct_str'].iloc[2]
    game_date = game_wp['game_date'].iloc[0].strftime('%#m/%#d/%y')
    inning_1 = game_wp['inning'].iloc[0]
    inning_2 = game_wp['inning'].iloc[1]
    inning_3 = game_wp['inning'].iloc[2]
    inning_1_suffix = suffix_dict[inning_1]
    inning_2_suffix = suffix_dict[inning_2]
    inning_3_suffix = suffix_dict[inning_3]
    topbot_1 = game_wp['inning_topbot'].iloc[0]
    topbot_2 = game_wp['inning_topbot'].iloc[1]
    topbot_3 = game_wp['inning_topbot'].iloc[2]
    
    # use functions to get other info
    series, game_num = get_series_game(game_wp)
    pre_bat1_1, pre_bat2_1, pre_fld1_1, pre_fld2_1, post_bat1_1, post_bat2_1, post_fld1_1, post_fld2_1 = get_score_change(game_wp, 0)
    pre_bat1_2, pre_bat2_2, pre_fld1_2, pre_fld2_2, post_bat1_2, post_bat2_2, post_fld1_2, post_fld2_2 = get_score_change(game_wp, 1)
    pre_bat1_3, pre_bat2_3, pre_fld1_3, pre_fld2_3, post_bat1_3, post_bat2_3, post_fld1_3, post_fld2_3 = get_score_change(game_wp, 2)
    #score_1 = get_score_change(game_wp, 0)
    #score_2 = get_score_change(game_wp, 1)
    #score_3 = get_score_change(game_wp, 2)
    
    # download base template
    img = Image.open('graphics\graphicTemplate.png')
    d1 = ImageDraw.Draw(img)
    
    # create colors
    gold = (255, 192, 0)
    white = (255, 255, 255)
    
    # create texts
    team_date_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 50)
    date_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 30)
    player_1_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 45)
    player_23_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 40)
    outcome_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 35)
    #percentage_1_font = ImageFont.truetype('graphics\\fonts\\helsinki.ttf', 100)
    #percentage_23_font = ImageFont.truetype('graphics\\fonts\\helsinki.ttf', 60)
    percentage_1_font = ImageFont.truetype('graphics\\fonts\\ChunkFivePrint.otf', 100)
    percentage_23_font = ImageFont.truetype('graphics\\fonts\\ChunkFivePrint.otf', 60)
    game_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 40)
    percent_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 30)
    series_game_font = ImageFont.truetype('graphics\\fonts\\Furore.otf', 70)
    score_font = ImageFont.truetype('graphics\\fonts\\digital-7(mono).ttf', 40)
    scoreboard_team_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 18)
    
    # TODO add texts to template
    if winner==team_names_dict[home_team]:
        d1.text((55, 30), f"{team_names_dict[away_team]} ({away_final}) @ ", font=team_date_font, fill=white)
        length = d1.textlength(text=f"{team_names_dict[away_team]} ({away_final}) @ ", font=team_date_font)
        d1.text((55+length, 30), f"{winner} ({home_final})", font=team_date_font, fill=gold)
    else:
        d1.text((55, 30), f"{winner} ({away_final}) ", font=team_date_font, fill=gold)
        length = d1.textlength(text=f"{winner} ({away_final}) ", font=team_date_font)
        d1.text((55+length, 30), f"@ {team_names_dict[home_team]} ({home_final})", font=team_date_font, fill=white)
    
    # PLAYER NAMES
    d1.text((930-20, 20), f"{game_date}", font=date_font, fill=white, anchor='rt')
    d1.text((202, 355), f"{player_1}", font=player_1_font, fill=gold)
    d1.text((105, 587), f"{player_2}", font=player_23_font, fill=white)
    d1.text((105, 804), f"{player_3}", font=player_23_font, fill=white)
    
    # EVENT and INNING
    d1.text((220, 415), f"{event_1} ({topbot_1} {inning_1}{inning_1_suffix})", font=outcome_font, fill=white)
    d1.text((125, 640), f"{event_2} ({topbot_2} {inning_2}{inning_2_suffix})", font=outcome_font, fill=white)
    d1.text((125, 857), f"{event_3} ({topbot_3} {inning_3}{inning_3_suffix})", font=outcome_font, fill=white)
    
    # SCORES
    
    # HOME TEAM
    d1.text((253, 479), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((156, 698), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((156, 916), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    
    d1.text((429, 479), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((333, 698), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((333, 916), f"{home_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    
    # AWAY TEAM
    d1.text((312, 479), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((215, 698), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((215, 916), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    
    d1.text((488, 479), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((392, 698), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    d1.text((392, 916), f"{away_team}", font=scoreboard_team_font, fill=gold, anchor='ma')
    
    # PLAYER 1
    d1.text((232, 508), f"{pre_bat1_1}", font=score_font, fill=white)
    d1.text((255, 508), f"{pre_bat2_1}", font=score_font, fill=white)
    d1.text((291, 508), f"{pre_fld1_1}", font=score_font, fill=white)
    d1.text((314, 508), f"{pre_fld2_1}", font=score_font, fill=white)
    d1.text((409, 508), f"{post_bat1_1}", font=score_font, fill=white)
    d1.text((433, 508), f"{post_bat2_1}", font=score_font, fill=white)
    d1.text((467, 508), f"{post_fld1_1}", font=score_font, fill=white)
    d1.text((490, 508), f"{post_fld2_1}", font=score_font, fill=white)
    
    # PLAYER 2
    d1.text((136, 727), f"{pre_bat1_2}", font=score_font, fill=white)
    d1.text((159, 727), f"{pre_bat2_2}", font=score_font, fill=white)
    d1.text((195, 727), f"{pre_fld1_2}", font=score_font, fill=white)
    d1.text((218, 727), f"{pre_fld2_2}", font=score_font, fill=white)
    d1.text((313, 727), f"{post_bat1_2}", font=score_font, fill=white)
    d1.text((337, 727), f"{post_bat2_2}", font=score_font, fill=white)
    d1.text((372, 727), f"{post_fld1_2}", font=score_font, fill=white)
    d1.text((395, 727), f"{post_fld2_2}", font=score_font, fill=white)
    
    # PLAYER 3
    d1.text((136, 945), f"{pre_bat1_3}", font=score_font, fill=white)
    d1.text((159, 945), f"{pre_bat2_3}", font=score_font, fill=white)
    d1.text((195, 945), f"{pre_fld1_3}", font=score_font, fill=white)
    d1.text((218, 945), f"{pre_fld2_3}", font=score_font, fill=white)
    d1.text((313, 945), f"{post_bat1_3}", font=score_font, fill=white)
    d1.text((337, 945), f"{post_bat2_3}", font=score_font, fill=white)
    d1.text((372, 945), f"{post_fld1_3}", font=score_font, fill=white)
    d1.text((395, 945), f"{post_fld2_3}", font=score_font, fill=white)
            
    # PROBABILITIES
    d1.text((865, 357), f"{pct_1}", font=percentage_1_font, fill=gold, anchor='ra')
    d1.text((655, 618), f"{pct_2}", font=percentage_23_font, fill=white, anchor='ra')    
    d1.text((655, 835), f"{pct_3}", font=percentage_23_font, fill=white, anchor='ra')
            
    # PERCENT SIGN
    d1.text((870, 399), "%", font=percent_font, fill=gold)
    d1.text((660, 630), "%", font=percent_font, fill=white)
    d1.text((660, 846), "%", font=percent_font, fill=white)
            
    if series=='WS':
        start_y = 750
        for char in series:
            d1.text((765, start_y), f"{char}", font=series_game_font, fill=white, anchor='ma')
            start_y += 90
    else:
        start_y = 675
        for char in series:
            d1.text((765, start_y), f"{char}", font=series_game_font, fill=white, anchor='ma')
            start_y += 80
            
    start_y = 675
    count = 1
    for char in game_num:
        if count==5:
            d1.text((845, start_y), f"{char}", font=series_game_font, fill=gold, anchor='ma')
        else:
            d1.text((845, start_y), f"{char}", font=series_game_font, fill=white, anchor='ma')
        start_y += 60
        count += 1
    
    # TODO save created graphic
    img.save(f"graphics\\created_graphics\\2022\\{((date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')).replace('/','-')}_{home_team}-{away_team}.png")
    img.show()
    

# create all graphics
win_prob_graphics(df)


def other_graphics(df):
    
    game_IDs = list(df.game_pk.unique())
    for game in game_IDs:
        game_df = df[df.game_pk==game]
        winner, home_final, away_final = get_winner(game_df)
        game_wp = win_prob_v2(game_df, extra=True)
        away_team = game_df.away_team.iloc[0]
        home_team = game_df.home_team.iloc[0]
        series, game_num = get_series_game(game_wp)
        
        create_graphic(game_wp, away_team, home_team, winner, home_final, away_final, series, game_num)


def create_other_graphic(df, homer, pitch, ev):
    
    # homer
    player_1 = homer['batter_name'].iloc[0]
    value_1 = homer['hit_distance_sc'].iloc[0]
    team_temp = homer['batter_team'].iloc[0]
    game_df_1 = df[(df.home_team==team_temp) | (df.away_team==team_temp)]
    winner_1, home_final_1, away_final_1 = get_winner(game_df_1)
    away_team_1 = game_df_1.away_team.iloc[0]
    home_team_1 = game_df_1.home_team.iloc[0]
    series_1, game_num_1 = get_series_game(game_df_1)
    game_date = game_df_1['game_date'].iloc[0].strftime('%#m/%#d/%y')
    
    # pitch
    player_2 = pitch['pitcher_name'].iloc[0]
    value_2 = pitch['release_speed'].iloc[0]
    team_temp = pitch['batter_team'].iloc[0]
    game_df_2 = df[(df.home_team==team_temp) | (df.away_team==team_temp)]
    winner_2, home_final_2, away_final_2 = get_winner(game_df_2)
    away_team_2 = game_df_2.away_team.iloc[0]
    home_team_2 = game_df_2.home_team.iloc[0]
    series_2, game_num_2 = get_series_game(game_df_2)
    
    # ev
    player_3 = ev['batter_name'].iloc[0]
    value_3 = ev['launch_speed'].iloc[0]
    team_temp = ev['batter_team'].iloc[0]
    game_df_3 = df[(df.home_team==team_temp) | (df.away_team==team_temp)]
    winner_3, home_final_3, away_final_3 = get_winner(game_df_3)
    away_team_3 = game_df_3.away_team.iloc[0]
    home_team_3 = game_df_3.home_team.iloc[0]
    series_3, game_num_3 = get_series_game(game_df_3)
    
    
    # download base template
    img = Image.open('graphics\graphicTemplateOther.png')
    d1 = ImageDraw.Draw(img)
    
    # create colors
    gold = (255, 192, 0)
    white = (255, 255, 255)
    
    # create fonts
    team_date_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 30)
    date_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 40)
    player_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 40)
    #outcome_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 35)
    game_font = ImageFont.truetype('graphics\\fonts\\OpenSans-Bold.ttf', 40)
    outcome_font = ImageFont.truetype('graphics\\fonts\\Furore.otf', 70)
    outcome_font_23 = ImageFont.truetype('graphics\\fonts\\Furore.otf', 55)
    
    # add texts to template
    x = 490
    y1 = 415
    y2 = 675
    y3 = 930
    if winner_1==team_names_dict[home_team_1]:
        d1.text((x, y1), f"{team_names_dict[away_team_1]} ({away_final_1}) @ ", font=team_date_font, fill=white)
        length = d1.textlength(text=f"{team_names_dict[away_team_1]} ({away_final_1}) @ ", font=team_date_font)
        d1.text((x+length, y1), f"{winner_1} ({home_final_1})", font=team_date_font, fill=gold)
    else:
        d1.text((x, y1), f"{winner_1} ({away_final_1}) ", font=team_date_font, fill=gold)
        length = d1.textlength(text=f"{winner_1} ({away_final_1}) ", font=team_date_font)
        d1.text((x+length, y1), f"@ {team_names_dict[home_team_1]} ({home_final_1})", font=team_date_font, fill=white)
        
    if winner_2==team_names_dict[home_team_2]:
        d1.text((x, y2), f"{team_names_dict[away_team_2]} ({away_final_2}) @ ", font=team_date_font, fill=white)
        length = d1.textlength(text=f"{team_names_dict[away_team_2]} ({away_final_2}) @ ", font=team_date_font)
        d1.text((x+length, y2), f"{winner_2} ({home_final_2})", font=team_date_font, fill=gold)
    else:
        d1.text((x, y2), f"{winner_2} ({away_final_2}) ", font=team_date_font, fill=gold)
        length = d1.textlength(text=f"{winner_2} ({away_final_2}) ", font=team_date_font)
        d1.text((x+length, y2), f"@ {team_names_dict[home_team_2]} ({home_final_2})", font=team_date_font, fill=white)
        
    if winner_1==team_names_dict[home_team_3]:
        d1.text((x, y3), f"{team_names_dict[away_team_3]} ({away_final_3}) @ ", font=team_date_font, fill=white)
        length = d1.textlength(text=f"{team_names_dict[away_team_3]} ({away_final_3}) @ ", font=team_date_font)
        d1.text((x+length, y3), f"{winner_3} ({home_final_3})", font=team_date_font, fill=gold)
    else:
        d1.text((x, y3), f"{winner_3} ({away_final_3}) ", font=team_date_font, fill=gold)
        length = d1.textlength(text=f"{winner_3} ({away_final_3}) ", font=team_date_font)
        d1.text((x+length, y3), f"@ {team_names_dict[home_team_3]} ({home_final_3})", font=team_date_font, fill=white)
    
    # PLAYER NAMES
    d1.text((720, 25), f"{game_date}", font=date_font, fill=white, anchor='ma')
    d1.text((690, 275), f"{player_1}", font=player_font, fill=gold, anchor='ma')
    d1.text((690, 535), f"{player_2}", font=player_font, fill=gold, anchor='ma')
    d1.text((690, 790), f"{player_3}", font=player_font, fill=gold, anchor='ma')
    
    # SERIES GAMES
    d1.text((490, 375), f"{series_1} Game {game_num_1[-1]}", font=team_date_font, fill=white)
    d1.text((490, 635), f"{series_2} Game {game_num_2[-1]}", font=team_date_font, fill=white)
    d1.text((490, 890), f"{series_3} Game {game_num_3[-1]}", font=team_date_font, fill=white)
            
    # VALUES
    start_y = 220
    for char in str(value_1):
        d1.text((405, start_y), f"{char}", font=outcome_font, fill=white, anchor='ma')
        start_y += 80
        
    start_y = 480
    for count, char in enumerate(str(value_2)):
        d1.text((405, start_y), f"{char}", font=outcome_font_23, fill=white, anchor='ma')
        if count==2:
            start_y+=20
        else:
            start_y += 50
        
    start_y = 735
    for count, char in enumerate(str(value_3)):
        d1.text((405, start_y), f"{char}", font=outcome_font_23, fill=white, anchor='ma')
        if count==2:
            start_y+=20
        else:
            start_y += 50
            
    # TODO save created graphic
    img.save(f"graphics\\created_graphics\\2022\\{((date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')).replace('/','-')}_summary.png")
    img.show()
    

create_other_graphic(df, homer_distance_high, pitch_speed_high, launch_speed_high)

tweets.append([
    f"2022 MLB Playoffs\n{(date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')} Statcast Leaders\n\n#Postseason",
    f"{(date.today() - timedelta(days=1)).strftime('%#m/%#d/%y').replace('/', '-')}_summary.png"
])


# # Publish Tweets

# ## Original Approach (No Media Upload Option)

# create client
client = tweepy.Client(
    bearer_token=statcast_secrets.bearer_token, 
    consumer_key=statcast_secrets.api_key, 
    consumer_secret=statcast_secrets.api_key_secret, 
    access_token=statcast_secrets.access_token, 
    access_token_secret=statcast_secrets.access_token_secret, 
    return_type = requests.Response,
    wait_on_rate_limit=True
)


# send tweets
for tweet in tweets:
    try:
        client.create_tweet(text=tweet)
    except:
        client.create_tweet(text=tweet[:270])


# ## New Approach (Need Elevated Access)

# # Setup Tweepy API
# auth = tweepy.OAuthHandler(consumer_key=statcast_secrets.api_key, consumer_secret=statcast_secrets.api_key_secret)
# auth.set_access_token(key=statcast_secrets.access_token, secret=statcast_secrets.access_token_secret)
# api = tweepy.API(auth)

# # send tweets
# for tweet in tweets[0:1]:
#     # Upload media to Twitter
#     file_path = f"graphics\\graphics\\2022\\{tweet[1]}"
#     ret = api.media_upload(file_path)
#     api.update_status(media_ids=[ret.media_id_string], status=tweet[0])
#     time.sleep(1)




