#!/usr/bin/env python
"""
#==============================================================================================
# megamillions Frequency analyzer and quick pick
# basically a python re-write of
# Mega Millions version of https://github.com/lwturkjr/Python_Powerball
# There isn't much difference aside the number ranges used, and the latest rule change
# was in October of 2017
# Author: Lloyd Turk Jr.
#==============================================================================================
"""

import random
import os
#from base64 import b64encode
#import urllib
import urllib.request as ur
import json
#import time
from datetime import datetime, date
#from collections import defaultdict

import pandas as pd

#START_TIME = time.time()
"""
#SYSTEM_RANDOM = os.urandom # Gives DeprecationWarning: Seeding based on hashing is deprecated
since Python 3.9 and will be removed in a subsequent version. The only 
supported seed types are: None, int, float, str, bytes, and bytearray.
random.seed(SYSTEM_RANDOM)
"""
SYSTEM_RANDOM = os.urandom(64) # Seems to resolve this
#seed = b64encode(SYSTEM_RANDOM).decode('utf-8') # This was another option to resolve it then random.seed(str(seed))
random.seed(SYSTEM_RANDOM)

def get_drawing_history():
    """Get the data from online"""
    # https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002
    url = "https://data.ny.gov/api/views/5xaw-6ayf/rows.json" # It's on data.gov from NY
    response = ur.urlopen(url)
    json_data = json.loads(response.read())
    #print(json_data.keys())

    raw_data = json_data["data"]
    raw_list = [] #
    for i in raw_data:
        raw_list.extend((i[8], i[9], i[10]))
    
#    print(raw_list)

    chunked_data_list = []
    for i in range(0, len(raw_list), 3):
        chunk = raw_list[i:i + 3]
        chunked_data_list.append(chunk)
    
#    print(chunked_data_list)

    final_data_list = []
    for i in chunked_data_list: # This works, it seems like it could still be more optimized though
        raw_date_time_str = i[0] # Raw date/time string from the json
        # Cleaned up date/time string
        date_time_str = datetime.strptime(raw_date_time_str, "%Y-%m-%dT%H:%M:%S")
        # Get rid of time part, we don't need it, I'm sure there is an easier/lighter way to do this
        # but this works for now
        date_str = date_time_str.strftime("%Y-%m-%d")

        final_data_list.append([date_str, i[1], i[2]])

    #print(final_data_list)
    return final_data_list

def quick_pick():
    """Quickpick function"""
    nums = []
    count = 1
    while count <= 5: # we need 5 numbers
        pick = random.randint(1, 70) # From 1 to 70
        # If pick isn't in the nums list, append the pick to the nums list,
        # it would return occasional dupes, this should fix that.
        if pick not in nums:
            nums.append(pick) # Append them to the list
            count = count+1
        else: # Don't add anything to count
            pass
    nums.sort() # Sort list for readability, makes it easier when filling out the number slips

    mega_ball = random.randint(1, 25)

    print("========================================================================")
    print("Random quick pick numbers: " + str(nums) +" "+ str(mega_ball))

def get_dates():
    """Analyze frequency of numbers"""
    # For custom date input
    #oldest_date = str(input("Input the oldest date in YYYY-MM-DD format: "))
    #newest_date = str(input("Input the newest date in YYYY-MM-DD format:"))
    #oldest_date = "2022-01-04" # First drawing of this year
    oldest_date = "2017-10-28" # This is the latest rule change
    #oldest_date = "2002-05-17" # The oldest date the data set goes back to
    #newest_date = "2022-07-26" # If you want to define a specific date range

    today = date.today()

    dates = pd.date_range(start=oldest_date, end=today) # Get a date range using pandas
    #dates = pd.date_range(start=oldest_date, end=newest_date) # For custom date range

    return dates

def dates_to_list():
    """Converts the pandas date_range into a list. This might not be necessary?"""
    dates = get_dates()
    date_list = []
    for date_time_obj in dates:
        date_str = date_time_obj.strftime("%Y-%m-%d")
        date_list.append(date_str)

    return date_list

def get_split_ball_list():
    """Split up the ball list to work with in later functions"""
    data = get_drawing_history()
    date_list = dates_to_list()

    ball_list = [] # This is a list, of strings being "int int int int int int"
    for i in data:
        if i[0] in date_list:
            ball_list.append(i[1] + " " + i[2])
    #print(ball_list)

    # We split these strings into lists of strings ["int", "int", "int", "int", "int", "int"], [...]
    split_list = []
    for i in ball_list:
        split = i.split()
        split_list.append(split)

    split_ball_list = [] # We turn this list of lists into a single list of strings
    for i in split_list:
        for j in i:
            split_ball_list.append(int(j))
            # We want the data in the list to be int, to use comparative operations later
    
    #print(split_ball_list)

    return split_ball_list
   

def get_ball_frequency():
    """"Analyze the frequency of balls being picked"""
    split_ball_list = get_split_ball_list()

    mb_list = split_ball_list[5::6] # Megaball is going to be every 6th entry in the list

    # To get white ball nums we now delete every 6th entry, which is the megaball
    del split_ball_list[5::6]

    white_ball_list = split_ball_list # Assign to a new list name, for ease of programming


    white_ball_list.sort() # Sort the list, this makes the dict we convert it to later more readable
    mb_list.sort() # Sort the list, this makes the dict we convert it to later more readable

    #unique_mb_list = list(set(mb_list))
    #unique_wb_list = list(set(white_ball_list))

    white_ball_dict = {i:white_ball_list.count(i) for i in white_ball_list}
    mb_dict = {i:mb_list.count(i) for i in mb_list}

    # Find the most commonly drawn MegaBall number
    mb_max_value = max(mb_dict.values()) 

    # Maximum secondary value for MB
    mb_max_secondary = 0
    for i in mb_dict.values(): # Find the second most commonly drawn MegaBall number
        if(i > mb_max_secondary and i < mb_max_value):
            mb_max_secondary = i

    # Find the least commonly drawn MegaBall number(s)
    # Need to add something to find 0 values
    mb_min_value = min(mb_dict.values())

    # Find the most commonly drawn white ball numbers
    wb_max_value = max(white_ball_dict.values())

    # Find the second most commonly drawn white ball numbers
    wb_max_secondary = 0
    for i in white_ball_dict.values(): 
        if(i > wb_max_secondary and i < wb_max_value):
            wb_max_secondary = i

    # Find the least commonly drawn white ball numbers
    # Need to add something to find 0 values
    wb_min_value = min(white_ball_dict.values())

    print("========================================================================")
    print("All numbers drawn for MegaBall with number of times drawn, in given date range")
    print("Number:Number of times drawn")
    print(mb_dict)
    #for key, value in mb_dict.items(): # Print all MB and number of times drawn
    #    print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Most commonly drawn MegaBall(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in mb_dict.items():
        if value == mb_max_value: # Print MB(s) with highest draw rate
            print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Second most commonly drawn MegaBall(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in mb_dict.items():
        if value == mb_max_secondary: # Print MB(s) with second highest draw rate
            print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Least commonly drawn MegaBall(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in mb_dict.items():
        if value == mb_min_value: # Print MB(s) with lowest draw rate
            print(str(key) + ":" + str(value))
    #================================================================================#
    print("========================================================================")
    print("All numbers drawn with number of times drawn, in given date range")
    print("Number:Number of times drawn")
    print(white_ball_dict)
    #for key, value in white_ball_dict.items(): # Print all white balls and number of times drawn
    #    print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Most commonly drawn number(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in white_ball_dict.items():
        if value == wb_max_value: # Print wb(s) with highest draw rate
            print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Second most commonly drawn number(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in white_ball_dict.items():
        if value == wb_max_secondary: # Print wb(s) with second highest draw rate
            print(str(key) + ":" + str(value))
    print("========================================================================")
    print("Least commonly drawn number(s) since given date: ")
    print("Number:Number of times drawn")
    for key, value in white_ball_dict.items():
        if value == wb_min_value: # Print wb(s) with lowest draw rate
            print(str(key) + ":" + str(value))
    print("========================================================================")
    print('This program is just for frequency analysis and a "Quick Pick" random'
          '\nnumber generator making no pretense at predictive accuracy')


quick_pick()
get_ball_frequency()

# For debugging to make sure it didn't take too long to run
#print("--- %s seconds ---" % (time.time() - START_TIME))
