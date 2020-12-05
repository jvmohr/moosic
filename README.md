# moosic

Very much in-progress. (Update: Not anymore.)

## Update

Likely won't be updated any longer as Google Play Music has been canned by Google. 

## Overview

Uses data user has to get from https://takeout.google.com/?hl=en to compute statistics. 

python convert_data.py mon year 
where mon is the first three letters of a month that this data is for and year is the full year (2020). 
This converts the data from Google into a DataFrame and saves it. Certain prompts may pop up if some artist names are similar (ex. Bastille and BASTILLE).  
Note: Data for December is also saved as end of the year data.  
Note: The data is thought of as being from the end of a month. 

moosic.py will be the driver for functions.py. 

