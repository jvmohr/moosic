# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:49:39 2020

@author: Joseph
"""

# Imports
import pandas as pd
import os
import json

global current

def open_data(name=""):
    """
    default is most recent
    otherwise "nov_2019" or just "2019" for the end of the year

    """
    if name == "":
        f = open("most_recent.txt", "r")
        nam = f.read()
        current = nam[9:-4]
        return pd.read_pickle(nam)
    else:
        current = name
        return pd.read_pickle(os.path.join("data", "end_"+name+".pkl"))


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