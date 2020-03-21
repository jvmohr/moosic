# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:26:18 2020

@author: Joseph
"""

# Imports - hi
import os
import pandas as pd
import html
import sys
import json
import functions 

if len(sys.argv) != 3:
    print("Wrong number of arguments")
    print("Expecting....  python convert_data.py mon year")
    sys.exit()

month = sys.argv[1]
year = sys.argv[2]
fold = os.path.join("end_month", "end_"+month+'_'+year, "Tracks") # where new data is
tracks = os.listdir(fold) # get all the file names

# Get previously stored songs
if not os.path.exists("songs.json"):
    f = open("songs.json", "w")
    json.dump({}, f)
    f.close()
f = open("songs.json", "r")
songs = json.load(f)
f.close()

# read in each track
total = []
track_num = {}
for track in tracks:
    place_holder = pd.read_csv(open(os.path.join(fold, track), 'r', encoding='utf-8'))
    title = place_holder['Title'][0]
    curr_song = str(place_holder['Title'][0]) + str(place_holder['Album'][0]) + str(place_holder['Artist'][0]) + str(place_holder['Duration (ms)'][0])
    curr_song = curr_song.upper() # to get rid of inconsistencies w/ data from Google
    curr_song = html.unescape(curr_song)
    
    if title in track_num:
        track_num[title] += 1
    else:
        track_num[title] = 1
    
    if curr_song in songs.keys():
        place_holder["Title"] = songs[curr_song]
    else:
        # find a name
        if str(place_holder['Title'][0]) in songs.values():
            i = 1
            while True:
                working_title = str(place_holder['Title'][0]) + "(" + str(i) + ")"
                if working_title in songs.values():
                    i += 1
                    continue
                songs[curr_song] = working_title
                place_holder['Title'] = working_title
                break
        else:
            songs[curr_song] = str(place_holder['Title'][0])
    
    total.append(place_holder)
    
end_of_year_df = pd.concat(total)

# save all songs 
f = open("songs.json", "w")
json.dump(songs, f)
f.close()

# Drop columns & escape html
working_df = end_of_year_df.drop(['Rating', 'Removed'], axis=1)
working_df['Title'] = working_df['Title'].astype(str).apply(html.unescape)
working_df['Album'] = working_df['Album'].astype(str).apply(html.unescape)
working_df['Artist'] = working_df['Artist'].astype(str).apply(html.unescape)
working_df.set_index('Title', inplace=True) # move song name to index

working_df['Total Duration'] = working_df['Duration (ms)'] * working_df['Play Count']

# For artist names with different capitalization
if not os.path.exists("capital.json"):
    f = open("capital.json", "w")
    json.dump({}, f)
    f.close()
f = open("capital.json", "r")
changes = json.load(f)
f.close()

# Go through current saved changes
for key in changes:
    working_df['Artist'] = working_df['Artist'].str.replace(changes[key], key)

# Perhaps save these in the future
while True:
    changed = False
    data2 = working_df['Artist'].unique()
    for artist in data2:
        if changed:
            break
        for item in data2:
            if artist != item:
                if artist.lower() == item.lower():
                    print(artist, " and ", item, "are similar.")
                    print("To change all of one to the other, select 1 or 2 to keep.")
                    answer = input("(1)"+ artist+ "  (2)"+ item+ " (3)keep separate:  ")
                    if int(answer) == 1:
                        working_df['Artist'] = working_df['Artist'].str.replace(item, artist)
                        changes[artist] = item
                        changed=True
                    if int(answer) == 2:
                        working_df['Artist'] = working_df['Artist'].str.replace(artist, item)
                        changes[item] = artist
                        changed=True
                    
    if not changed:
        break

f = open("capital.json", "w")
json.dump(changes, f)
f.close()
    
# Save data to pickle
working_df.to_pickle(os.path.join("data", "end_"+month+'_'+year+".pkl"))
print(os.path.join("data", "end_"+month+'_'+year+".pkl"), " written successfully")

if month == 'dec':
    working_df.to_pickle(os.path.join("data", "end_"+year+".pkl"))
    print(os.path.join("data", "end_"+year+".pkl"), " written successfully")

f = open('most_recent.txt', 'w')
f.write(os.path.join("data", "end_"+month+'_'+year+".pkl"))
f.close()

# Read
#hello = pd.read_pickle(os.path.join("data", "end_"+month+'_'+year+".pkl"))

# play_df = working_df.sort_values(by='Play Count', ascending=False)
# play_df[play_df['Play Count'] >= 250]