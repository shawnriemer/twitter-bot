import pandas as pd
import os


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

def fix_names(name_comma):
    parts = name_comma.split(',')
    return parts[-1][1:] + ' ' + parts[0]


def load_data(file):
    """This function creates the DataFrame for a specified file"""
    
    df = pd.read_csv(file)
    df = df.rename(columns={'player_name':'batter_name'})
    file_pitcher = os.path.join('data', 'pitcher_data', (file[5:-4] + '_pitcher.csv'))
    pi = pd.read_csv(file_pitcher)

    df['batter_team'] = df.apply (lambda row: add_batter_team(row), axis=1)
    pi['pitcher_team'] = pi.apply (lambda row: add_pitcher_team(row), axis=1)
    # pi = pi[['player_name', 'pitcher_team']].rename(columns={'player_name':'pitcher_name'})

    # df = df.merge(pi, left_index=True, right_index=True)

    pi = pi.rename(columns={'player_name':'pitcher_name'})
    df = df.merge(pi[['pitcher_name', 'pitcher_team', 'release_speed', 'release_pos_x', 'release_pos_y', 'batter', 'pitcher', 'events', 'description']],
               on=['release_speed', 'release_pos_x', 'release_pos_y', 'batter', 'pitcher', 'events', 'description'])

    df['batter_name'] = df['batter_name'].apply(fix_names)
    df['pitcher_name'] = df['pitcher_name'].apply(fix_names)
         
    df = df[df.duplicated(subset=['pitcher_name', 'release_speed', 'release_pos_x', 'release_pos_y',
                                  'description', 'release_spin_rate']) == False]

    return df



def launch_speed(df, n=5, bottom=False, all_data=False, only_events=False, date=False):
    """This function returns the extreme exit velocities of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between highest and lowest exit velocities.
    all_data returns every result, but sorted.
    only_events can be used to filter by pitches ending in an event.
    """
    
    launch = df.dropna(subset=['launch_speed']).sort_values(by='launch_speed', ascending=bottom)
    
    if only_events:
        launch = launch[launch.events.notnull()]
        
    if date:
        launch = launch[['batter_name', 'batter_team', 'launch_speed', 'launch_angle', 'events',
                     'description', 'pitch_type', 'pitcher_name', 'pitcher_team', 'game_date']]
    else:
        launch = launch[['batter_name', 'batter_team', 'launch_speed', 'launch_angle', 'events',
                     'description', 'pitch_type', 'pitcher_name', 'pitcher_team']]
        
    if all_data:
        return launch
    else:
        launch = launch.iloc[:n]
        return launch

    

def pitch_speed(df, n=5, bottom=False, all_data=False, only_events=False, unique=False, date=False):
    """This function returns the extreme pitch velocities of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between highest and lowest exit velocities.
    all_data returns every result, but sorted.
    only_events can be used to filter by pitches ending in an event.
    unique returns only 1 result per pitcher (unless their extreme pitch appeared more than once).
    """
    
    pitch = df.dropna(subset=['release_speed']).sort_values(by='release_speed', ascending=bottom)
    
    if only_events:
        pitch = pitch[pitch.events.notnull()]
        
    if date:
        pitch = pitch[['pitcher_name', 'pitcher_team', 'release_speed', 'launch_angle', 'events',
                   'description', 'pitch_type', 'batter_name', 'batter_team', 'game_date']]
    else:
        pitch = pitch[['pitcher_name', 'pitcher_team', 'release_speed', 'launch_angle', 'events',
                   'description', 'pitch_type', 'batter_name', 'batter_team']]
    
    if unique:
        if bottom:
            pitch = pitch[pitch.groupby(['pitcher_name'])['release_speed'].transform(min) == pitch['release_speed']]
        else:
            pitch = pitch[pitch.groupby(['pitcher_name'])['release_speed'].transform(max) == pitch['release_speed']]
    
    if all_data:
        return pitch
    else:
        pitch = pitch.iloc[:n]
        return pitch


    
def homer_distance(df, n=5, bottom=False, all_data=False, date=False, exclude_inside=False):
    """This function returns the extreme homer distances of the day.
    
    n controls how many results are returned.
    bottom can be used to switch between farthest and shortest homer distances.
    all_data returns every result, but sorted.
    """
    
    homers = df[df.events == 'home_run'].sort_values(by='hit_distance_sc', ascending=bottom)

    if exclude_inside:
        homers = homers[~homers.des.str.contains('inside')]
	
    if date:
        homers = homers[['batter_name', 'batter_team', 'hit_distance_sc', 'launch_angle',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type', 'game_date']]
    else:
        homers = homers[['batter_name', 'batter_team', 'hit_distance_sc', 'launch_angle',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type']]
    
    homers = homers.iloc[:n]
    
    return homers



def win_pct(df, n=5, all_data=False, date=False):
    """This function returns the largest changes in win percentage of the day.
    
    n controls how many results are returned.
    all_data returns every result, but sorted.
    """
    
    win_pct = df.copy(deep=True)
    win_pct['delta_home_win_exp'] = abs(win_pct['delta_home_win_exp'])*100
    win_pct = win_pct.sort_values(by='delta_home_win_exp', ascending=False)

    if date:
        win_pct = win_pct[['batter_name', 'batter_team', 'events', 'delta_home_win_exp',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type', 'game_date']]
    else:
        win_pct = win_pct[['batter_name', 'batter_team', 'events', 'delta_home_win_exp',
                   'pitcher_name', 'pitcher_team', 'release_speed', 'pitch_type']]
    
    win_pct = win_pct.iloc[:n]
    
    return win_pct



# swing types
every = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked', 'called_strike', 'foul', 'hit_into_play', 'foul_bunt']
swinging = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked', 'swinging_pitchout']
fouls = ['foul', 'foul_bunt']
contact = ['foul', 'foul_bunt', 'hit_into_play']
in_play = ['hit_into_play']
balls = ['ball', 'blocked_ball', 'hit_by_pitch']

def pitch_counts(df, n=5, all_data=False, strike_type=swinging, pitch_type=False, total=False, date=False):
    """This function returns the pitchers/pitch types with the most (swinging) strikes.
    
    n controls how many results are returned.
    all_data returns every result, but sorted.
    strike_type defines what subset of pitch outcomes are being counted. It can be predefined or custom.
    pitch_type defines what combination of pitcher and pitch type to consider.
    total simply returns total number of pitches thrown. It can be combined with pitch_type.
    """
    
    if total:
        counts = df
    else:
        counts = df[df.description.isin(strike_type)]
    
    if pitch_type:
        counts = counts.groupby(by=['pitcher_name', 'pitch_type']).count()
    else:
        counts = counts.groupby(by='pitcher_name').count()
        
    counts = counts[['description']].sort_values(by='description', ascending=False)
    
    counts.reset_index(inplace=True)
    
    return counts.iloc[:n]



def pitches_seen(df, n=5, atbat=False, pitch_type=False, date=False):
    """This function finds leaders in number of pitches seen on the day.
    
    n controls how many results are returned.
    atbat looks for the longest single atbats rather than the whole day. 
    pitch_type looks for the batters who saw the most of a specific pitch.
    """
    
    if atbat:
        grouped = df.groupby(by=['batter_name', 'batter_team', 'inning', 'outs_when_up', 'game_pk', 'game_date'])
        seen = grouped.count()[['pitch_type']].sort_values(by='pitch_type', ascending=False).reset_index().iloc[:n]
        
        event_list = []
        for i, row in seen.iterrows():
            df_new = df[(df.batter_name==row.batter_name)&(df.inning==row.inning)&(df.outs_when_up==row.outs_when_up)&(df.game_pk==row.game_pk)]
            event = df_new.iloc[0].events

            if pd.isnull(event):
                event = df_new[df_new.events.notnull()].events.iloc[0]

            event_list.append(event)
            
        seen['events'] = event_list
        
        return seen
    
    if pitch_type:
        seen = df.groupby(by=['batter_name', 'pitch_type']).count()[['description']].sort_values(by='description', ascending=False)
        seen.reset_index(inplace=True)
    else:
        seen = df.groupby(by='batter_name').count()[['description']].sort_values(by='description', ascending=False)
        seen.reset_index(inplace=True)
    
    return seen.iloc[:n]



def homer_launch_angle(df, n=5, low=False, date=False):
    """This function finds the highest/lowest launch angle on homers.
    
    n controls how many results are returned.
    low controls if the highest or lowest launch angle is returned. 
    """

    df = df[~df.des.str.contains('inside')]

    if date:
        homers = df[df.events=='home_run'][['batter_name', 'batter_team', 'launch_angle', 'hit_distance_sc',
                                       'launch_speed', 'pitcher_name', 'pitcher_team', 'game_date']]
    else:
        homers = df[df.events=='home_run'][['batter_name', 'batter_team', 'launch_angle', 'hit_distance_sc',
                                       'launch_speed', 'pitcher_name', 'pitcher_team']]
    
    la = homers.sort_values(by='launch_angle', ascending=low)
    
    return la.iloc[:n]



def spin_rate(df, n=5, low=False, pitch_type=None, date=False):
    """This function returns highest/lowest spin rate on pitches.
    
    n controls how many results are returned.
    low controls if the highest or lowest spin rate is returned.
    """
    
    df = df[pd.notnull(df.release_spin_rate)]
    
    if pitch_type != None:
        df = df[df.pitch_type==pitch_type]
        
    spin = df.sort_values(by='release_spin_rate', ascending=low)

    if date:
        spin = spin[['pitcher_name', 'pitcher_team', 'release_spin_rate', 'pitch_type',
                 'description', 'batter_name', 'batter_team', 'game_date']]
    else:
        spin = spin[['pitcher_name', 'pitcher_team', 'release_spin_rate', 'pitch_type',
                 'description', 'batter_name', 'batter_team']]
    
    spin['release_spin_rate'] = spin['release_spin_rate'].astype('int32')
    spin['description'] = spin['description'].str.replace('_', ' ')
    
    return spin.iloc[:n]



def pitch_move(df, n=5, low=False, vert=False, pitch_type=None):
    """This function returns pitches with the most horizontal/vertical movement.
    
    n controls how many results are returned.
    low controls if the highest or lowest spin rate is returned.
    vert controls if horizontal or vertical movement is used.
    pitch_type controls if the data is filtered by a specific pitch.
    """
    
    move = df.dropna(axis=0, subset=['pfx_x', 'pfx_z', 'release_spin_rate'])
    
    if pitch_type != None:
        move = move[move.pitch_type==pitch_type]
    
    if vert:
        move = move.reindex(move.pfx_z.abs().sort_values(ascending=low).index)
        move = move[['pitcher_name', 'pitcher_team', 'pfx_z', 'release_spin_rate', 'pfx_x', 'pitch_type',
                 'description', 'batter_name', 'batter_team', 'game_date']]
    else:
        move = move.reindex(move.pfx_x.abs().sort_values(ascending=low).index)
        move = move[['pitcher_name', 'pitcher_team', 'pfx_x', 'release_spin_rate', 'pfx_z', 'pitch_type',
                 'description', 'batter_name', 'batter_team', 'game_date']]
        
    
    return move.iloc[:n]



def wild_pitch(df, n=5, vert=False, low=False, pitch_type=None):
    """This function returns the most wild pitches by where they crossed the plate.
    
    n controls how many results are returned.
    vert controls if horizontal or vertical location is used.
    pitch_type controls if the data is filtered by a specific pitch.
    """
    
    wild = df.dropna(axis=0, subset=['plate_x', 'plate_z'])
    
    if pitch_type != None:
        wild = wild[wild.pitch_type==pitch_type]
    
    if vert:
        wild = wild.reindex(wild.plate_z.sort_values(ascending=low).index)
        wild = wild[['pitcher_name', 'pitcher_team', 'plate_z', 'release_speed', 'plate_x', 'pitch_type',
                 'description', 'batter_name', 'batter_team', 'game_date']]
    else:
        wild = wild.reindex(wild.plate_x.abs().sort_values(ascending=False).index)
        wild = wild[['pitcher_name', 'pitcher_team', 'plate_x', 'release_speed', 'plate_z', 'pitch_type',
                 'description', 'batter_name', 'batter_team', 'game_date']]
        
    return wild.iloc[:n]



def wild_homer(df, n=5, area='low'):
    """This function finds the most up/down/inside/outside pitches hit for homers.
    
    n controls how many results are returned.
    area controls which pitch direction to look at. 
    """

    homers = df[df.events=='home_run'][['batter_name', 'batter_team', 'stand', 'launch_angle', 'hit_distance_sc',
                                    'plate_z', 'plate_x', 'pitcher_name', 'pitcher_team', 'game_date']]
    
    if area=='low':
        return homers.sort_values(by='plate_z', ascending=True).iloc[:n]
    elif area=='high':
        return homers.sort_values(by='plate_z', ascending=False).iloc[:n]
    elif area=='outside':
        homersL = homers[homers.stand == 'L'].sort_values(by='plate_x', ascending=True).iloc[:n]
        homersR = homers[homers.stand == 'R'].sort_values(by='plate_x', ascending=False).iloc[:n]
        homers = pd.concat([homersL, homersR])
        homers['in_loc'] = homers['plate_x'].apply(abs)
        return homers.sort_values(by='in_loc', ascending=False).iloc[:n]
    elif area=='inside':
        homersL = homers[homers.stand == 'L'].sort_values(by='plate_x', ascending=False).iloc[:n]
        homersR = homers[homers.stand == 'R'].sort_values(by='plate_x', ascending=True).iloc[:n]
        homers = pd.concat([homersL, homersR])
        homers['out_loc'] = homers['plate_x'].apply(abs)
        return homers.sort_values(by='out_loc', ascending=False).iloc[:n]



def wild_swings(df, n=5, area='high'):
    """This function finds the most up/down/inside/outside pitches swung at.
    
    n controls how many results are returned.
    area controls which pitch direction to look at. 
    """

    swings = df[(df.description=='swinging_strike') | (df.description=='swinging_strike_blocked')][['batter_name', 'batter_team', 'stand', 'launch_angle', 'hit_distance_sc',
                                    'plate_z', 'plate_x', 'pitcher_name', 'pitcher_team', 'game_date', 'description', 'balls', 'strikes', 'inning']]
    
    if area=='low':
        return swings.sort_values(by='plate_z', ascending=True).iloc[:n]
    elif area=='high':
        return swings.sort_values(by='plate_z', ascending=False).iloc[:n]
    elif area=='outside':
        swingsL = swings[swings.stand == 'L'].sort_values(by='plate_x', ascending=True).iloc[:n]
        swingsR = swings[swings.stand == 'R'].sort_values(by='plate_x', ascending=False).iloc[:n]
        swings = pd.concat([swingsL, swingsR])
        swings['out_loc'] = swings['plate_x'].apply(abs)
        return swings.sort_values(by='out_loc', ascending=False).iloc[:n]
    elif area=='inside':
        swingsL = swings[swings.stand == 'L'].sort_values(by='plate_x', ascending=False).iloc[:n]
        swingsR = swings[swings.stand == 'R'].sort_values(by='plate_x', ascending=True).iloc[:n]
        swings = pd.concat([swingsL, swingsR])
        swings['in_loc'] = swings['plate_x'].apply(abs)
        return swings.sort_values(by='in_loc', ascending=False).iloc[:n]

