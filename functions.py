# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:49:39 2020

@author: Joseph
"""

# Imports - hi
import pandas as pd
import os
import json

global current
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 
          'sep', 'oct', 'nov', 'dec']

def open_data(name="", compress=False):
    """
    default is most recent
    otherwise "nov_2019" or just "2019" for the end of the year

    """
    if name == "":
        f = open("most_recent.txt", "r")
        nam = f.read()
        current = nam[9:-4]
        data = pd.read_pickle(nam)
    else:
        current = name
        data = pd.read_pickle(os.path.join("data", "end_"+name+".pkl"))
    
    if compress:
        data = compress_saved(data)
    return data


def total_plays(data):
    return data['Play Count'].sum()

def plays_by_artist(data, artist, just=0):
    """
    just = 0 means all songs where artist appears in the artist string
    just = 1 means all songs where artist.lower() is == artist string.lower()
    just = 2 means only exact matches
    """
    # just = 1, 2 not tested
    if just == 0:
        artist = artist.lower()
        return data[data['Artist'].apply(lambda x: artist in x.lower())]['Play Count'].sum()
    elif just == 1:
        artist = artist.lower()
        return data[data['Artist'].apply(lambda x: artist == x.lower())]['Play Count'].sum()
    else:
        return data[data['Artist'].apply(lambda x: artist == x)]['Play Count'].sum()

def length_by_artist(data, artist=None, just=0, length='seconds'):
    """
    default in seconds
    just = 0 means all songs where artist appears in the artist string
    just = 1 means all songs where artist.lower() is == artist string.lower()
    just = 2 means only exact matches
    
    maybe allow artist to be a list
    """
    # just = 1, 2 not tested
    if length =='seconds':
        denom = 1000
    elif length == 'minutes':
        denom = 60000
    elif length == 'hours':
        denom = 3600000
    
    if artist == None:
        data2 =  data.groupby(['Artist']).sum()
        data2['Total Duration'] = data2['Total Duration'] / denom
        
        return data2.sort_values(by='Total Duration', ascending=False)
        
    if just == 0:
        artist = artist.lower()
        return data[data['Artist'].apply(lambda x: artist in x.lower())]['Total Duration'].sum()/denom
    elif just == 1:
        artist = artist.lower()
        return data[data['Artist'].apply(lambda x: artist == x.lower())]['Total Duration'].sum()/denom
    else:
        return data[data['Artist'].apply(lambda x: artist == x)]['Total Duration'].sum()/denom

def compress_artists(data, artist, save=True):
    artists = data['Artist'].unique()
    
    compress = artist.lower()
    to_compress = []
    
    # Find similar artists to be changed
    for item in artists:
        if compress in item.lower():
            to_compress.append(item)
    
    # so shenanigans don't occur
    to_compress.sort(key=lambda x: len(x), reverse=True) 
    
    # Change those artists
    for item in to_compress:
        data['Artist'] = data['Artist'].str.replace(item, artist, regex=False)
    
    if not save:
        return data
    # Save - bit messy
    if not os.path.exists("compress.json"):
        f = open("compress.json", "w")
        json.dump([], f)
        f.close()
    f = open("compress.json", "r")
    changes = json.load(f)
    f.close()
    changes.append({artist:to_compress})
    f = open("compress.json", "w")
    json.dump(changes, f)
    f.close()
    
    return data

def compress_saved(data):
    # compress
    f = open("compress.json", "r")
    changes = json.load(f)
    f.close()

    for item in changes: # for dict in list
        for artist in item: # for key in dict (only 1 key)
            for fake in item[artist]:
                data['Artist'] = data['Artist'].str.replace(fake, artist, regex=False)
    return data

def _get_last_month(month, year):
    i = months.index(month)
    return months[i-1]+"_"+year if i > 0 else months[11]+"_"+str(int(year)-1)

def get_month(name, length='hours', compress=True):
    this_month = open_data(name=name, compress=compress)
    last = _get_last_month(name[:3], name[4:])
    last_month = open_data(name=last, compress=compress)
    
    if length =='seconds':
        denom = 1000
    elif length == 'minutes':
        denom = 60000
    elif length == 'hours':
        denom = 3600000
        
    difference = this_month[['Album', 'Artist', 'Duration (ms)']].copy()
    difference.loc[:,'Play Count'] = this_month['Play Count'].subtract(last_month['Play Count'], axis=0, fill_value=0)
    difference.loc[:,'Total Duration'] = difference['Play Count'] * difference['Duration (ms)'] / denom
    return difference[ difference['Play Count'] > 0.0] # only tracks that were played

def month_statistics(month, compress=True, top=True, top_songs=0, top_albums=0, 
                       top_artists=0):
    # get the data
    diff = get_month(month) # in hours
    new_data = open_data(name=month, compress=compress)
    last = _get_last_month(month[:3], month[4:])
    old_data = open_data(name=last, compress=compress)
    print("Month: ", month[0].upper() + month[1:3] + " " + month[4:])
    
    # finds songs added in last month
    new_songs = new_data.index.drop(old_data.index)
    if len(new_songs) > 0:
        print("Songs Added: ")
        for song in list(new_songs):
            print("  ", song)
    
    # Overall statistics
    print("   Play Count:", diff.sum()['Play Count'])
    print("   Time in hours:", "{0:.2f}".format(diff.sum()['Total Duration']))
    
    # Songs that broke milestones (100, 200, etc.)
    max_plays = new_data['Play Count'].max()
    start = 100
    while start < max_plays:
        # get songs past milestone in current and previous months
        new_mile = new_data[ new_data['Play Count'] >= start ]
        old_mile = old_data[ old_data['Play Count'] >= start ]
        
        mile = new_mile.index.drop(list(old_mile.index)) # drop ones 
        if len(mile) > 0:
            print("Broke", start, "plays:")
            for song in list(mile):
                print("   ", song)
        start += 100
    
    # Song, Album, Artist top 1
    albums = diff.groupby(by='Album').sum().sort_values(by='Play Count', ascending=False)
    artists = diff.groupby(by='Artist').sum().sort_values(by='Play Count', ascending=False)
    if top:
        print("Top Song: ")
        _top_n(diff, 1, 'Play Count')
        _top_n(diff, 1, 'Total Duration')
        
        print("Top Album: ")
        _top_n(albums, 1, 'Play Count')
        _top_n(albums, 1, 'Total Duration')
        
        print("Top Artist: ")
        _top_n(artists, 1, 'Play Count')
        _top_n(artists, 1, 'Total Duration')
    
    # Song, Album, Artist top N 
    if top_songs > 0:
        print('Top', top_songs, 'Songs:')
        _top_n(diff, top_songs, 'Play Count')
    
    if top_albums > 0:
        print('Top', top_albums, 'Albums:')
        _top_n(albums, top_albums, 'Play Count')
        
    if top_artists > 0:
        print('Top', top_artists, 'Artists:')
        _top_n(artists, top_artists, 'Play Count')
    
    return

def _top_n(data, n, key='Play Count'):
    data.sort_values(by=key, ascending=False, inplace=True)
    for i in range(n):
        if key == 'Play Count':
            print("   ", int(data.iloc[i][key]), "plays:", data.index[i])
        elif key == 'Total Duration':
            print("   ", "{0:.2f}".format(data.iloc[i][key]), "hours:", data.index[i])
    return

def overall_statistics():
    data = open_data(compress=True) 
    data.loc[:,'Total Duration'] = data['Play Count'] * data['Duration (ms)'] / 3600000
    
    # Overall statistics
    print(data.sum()['Play Count'], 'plays')
    print("{0:.2f}".format(data.sum()['Total Duration']), 'hours')
    
    
    
    return

