import pandas as pd
import os
from datetime import date
from datetime import timedelta


def add_name(mlb_ID, player_data):
    player_row = player_data[player_data.key_mlbam==mlb_ID]
    try:
        full_name = f"{player_row['name_first'].iloc[0]} {player_row['name_last'].iloc[0]}"
    except:
        # players making their debuts may take a week to show up here
        return "Unknown"
    return full_name



def add_batter_team(row):
    if row.inning_topbot == 'Top':
        return row.away_team
    else:
        return row.home_team
    


def add_pitcher_team(row):
    if row.inning_topbot == 'Top':
        return row.home_team
    else:
        return row.away_team



def clean_data(df, player_data):
    df['batter_name'] = df['batter'].apply(add_name, args=(player_data,))
    df['pitcher_name'] = df['pitcher'].apply(add_name, args=(player_data,))
    df['batter_team'] = df.apply(lambda row: add_batter_team(row), axis=1)
    df['pitcher_team'] = df.apply(lambda row: add_pitcher_team(row), axis=1)
    df = df[df.duplicated(subset=['pitcher_name', 'release_speed', 'release_pos_x', 'release_pos_y',
                                  'description', 'release_spin_rate']) == False]
    df = df.drop(columns=['player_name'])
    return df



def homer_distance(df, n=5, bottom=False, all_data=False):
    """This function returns the extreme homer distances of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between farthest and shortest homer distances.
    all_data returns every result, but sorted.
    """
    
    homers = df[df.events == 'home_run'].sort_values(by='hit_distance_sc', ascending=bottom)

    homers = homers[['batter_name', 'batter_team', 'hit_distance_sc', 'launch_angle',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type', 'game_date']]
    
    homers = homers.iloc[:n]
    
    return homers



def pitch_speed(df, n=5, bottom=False, all_data=False, only_events=False, unique=False):
    """This function returns the extreme pitch velocities of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between highest and lowest exit velocities.
    all_data returns every result, but sorted.
    only_events can be used to filter by pitches ending in an event.
    unique returns only 1 result per pitcher.
    """
    
    pitch = df.dropna(subset=['release_speed']).sort_values(by='release_speed', ascending=bottom)
    
    if only_events:
        pitch = pitch[pitch.events.notnull()]
        
    pitch = pitch[['pitcher_name', 'pitcher_team', 'release_speed', 'launch_angle', 'events',
                   'description', 'pitch_type', 'batter_name', 'batter_team', 'game_date']]

    if unique:
        pitch = pitch[pitch.duplicated(subset=['pitcher_name']) == False]
    
    if all_data:
        return pitch
    else:
        pitch = pitch.iloc[:n]
        return pitch



def launch_speed(df, n=5, bottom=False, all_data=False, only_events=False):
    """This function returns the extreme exit velocities of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between highest and lowest exit velocities.
    all_data returns every result, but sorted.
    only_events can be used to filter by pitches ending in an event.
    """
    
    launch = df.dropna(subset=['launch_speed']).sort_values(by='launch_speed', ascending=bottom)
    
    if only_events:
        launch = launch[launch.events.notnull()]
        
    launch = launch[['batter_name', 'batter_team', 'launch_speed', 'launch_angle', 'events',
                     'description', 'pitch_type', 'pitcher_name', 'pitcher_team', 'game_date']]
        
    if all_data:
        return launch
    else:
        launch = launch.iloc[:n]
        return launch



def pitches_seen(df, n=5, atbat=False, pitch_type=False):
    """This function finds leaders in number of pitches seen on the day.
    
    n controls how many results are returned.
    atbat looks for the longest single atbats rather than the whole day. 
    pitch_type looks for the batters who saw the most of a specific pitch.
    """
    
    if atbat:
        grouped = df.groupby(by=['batter_name', 'batter_team', 'inning', 'outs_when_up', 'game_pk'])
        seen = grouped.count()[['pitch_type']].sort_values(by='pitch_type', ascending=False).reset_index().iloc[:n]
        
        event_list = []
        for i, row in seen.iterrows():
            df_new = df[(df.batter_name==row.batter_name)&(df.inning==row.inning)&(df.outs_when_up==row.outs_when_up)&(df.game_pk==row.game_pk)]
            event = df_new.iloc[0].events

            if pd.isnull(event):
                try:
                    event = df_new[df_new.events.notnull()].events.iloc[0]
                except IndexError:
                    event = "left for injury"

            event_list.append(event)
            
        seen['events'] = event_list
        
        return seen
    
    if pitch_type:
        seen = df.groupby(by=['batter_name', 'pitch_type']).count()[['description']].sort_values(by='description', ascending=False)
        seen.reset_index(inplace=True)
    else:
        seen = df.groupby(by=['batter_name', 'batter_team']).count()[['description']].sort_values(by='description', ascending=False)
        seen.reset_index(inplace=True)
    
    return seen.iloc[:n]



def win_prob(df, n=5, all_data=False, extra=False):
    """This function returns the largest changes in win percentage of the day.
    
    n controls how many results are returned.
    all_data returns every result, but sorted.
    """
    
    win_prob = df.copy(deep=True)
    win_prob = win_prob[~win_prob['events'].isna()]
    
    win_prob['delta_home_win_exp'] = abs(win_prob['delta_home_win_exp'])*100
    win_prob = win_prob.sort_values(by='delta_home_win_exp', ascending=False)

    if not extra:
        win_prob = win_prob[['batter_name', 'batter_team', 'events', 'delta_home_win_exp',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type', 'game_date']]
    
    win_prob = win_prob.iloc[:n]
    
    return win_prob





def create_homer_high_tweet(homer_distance_high, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')
        
    for i in range(3):
        name = homer_distance_high.iloc[i,0]
        team = homer_distance_high.iloc[i,1]
        distance = str(homer_distance_high.iloc[i,2])

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {distance} ft\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Longest Homers 💣\n({date_str})\n\n" + text
    
    return text



def create_homer_low_tweet(homer_distance_low, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = homer_distance_low.iloc[i,0]
        team = homer_distance_low.iloc[i,1]
        distance = str(homer_distance_low.iloc[i,2])

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {distance} ft\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Shortest Homers 📏\n({date_str})\n\n" + text

    return text



def create_pitch_high_tweet(pitch_speed_high, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = pitch_speed_high.iloc[i,0]
        team = pitch_speed_high.iloc[i,1]
        speed = pitch_speed_high.iloc[i,2]
        event = pitch_speed_high.iloc[i,5].replace('_', ' ')

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {speed} mph ({event})\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Fastest Pitches 🔥\n({date_str})\n\n" + text

    return text



def create_pitch_low_tweet(pitch_speed_low, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = pitch_speed_low.iloc[i,0]
        team = pitch_speed_low.iloc[i,1]
        speed = pitch_speed_low.iloc[i,2]
        event = pitch_speed_low.iloc[i,5].replace('_', ' ')

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {speed} mph ({event})\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Slowest Pitches 🐌\n({date_str})\n\n" + text

    return text



def create_ev_high_tweet(launch_speed_high, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = launch_speed_high.iloc[i,0]
        team = launch_speed_high.iloc[i,1]
        speed = launch_speed_high.iloc[i,2]
        event = launch_speed_high.iloc[i,4].replace('_', ' ')

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {speed} mph ({event})\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Highest Exit Velocity 🚀\n({date_str})\n\n" + text

    return text



def create_ev_low_tweet(launch_speed_low, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = launch_speed_low.iloc[i,0]
        team = launch_speed_low.iloc[i,1]
        speed = launch_speed_low.iloc[i,2]
        event = launch_speed_low.iloc[i,4].replace('_', ' ')

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {speed} mph ({event})\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Lowest Exit Velocity 🐢\n({date_str})\n\n" + text

    return text



def create_atbat_long_tweet(pitches_seen_atbat_high, socials):
    strings = []
    date_str = (date.today() - timedelta(days=1)).strftime('%#m/%#d/%y')

    for i in range(3):
        name = pitches_seen_atbat_high.iloc[i,0]
        team = pitches_seen_atbat_high.iloc[i,1]
        pitches = pitches_seen_atbat_high.iloc[i,5]
        event = pitches_seen_atbat_high.iloc[i,6].replace('_', ' ')

        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {pitches} ({event})\n    {socials[team]['hashtag']}\n"
        strings.append(string)

    text = '\n'.join(strings)
    text = f"Longest At-Bats [# of Pitches] ⏳\n({date_str})\n\n" + text

    return text



def create_win_prob_tweet(win_prob_high, socials):
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
        string = f"{str(i+1)}. {name} {socials[team]['at']}\n    {round(prob,1)}% ({event})\n    {socials[team]['hashtag']}\n"

        strings.append(string)

    text = '\n'.join(strings)
    text = f"Largest Changes in Win Probability 📈\n({date_str})\n\n" + text

    return text



