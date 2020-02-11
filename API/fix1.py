# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:42:51 2020

@author: swatkins
"""
​
import os, numpy as np
import pandas as pd
import numbers
import random
import csv
import json
import ast
from datetime import datetime as dt
from datetime import timedelta, date
import math
from flow import TrafficFlow
from location import Location
from Jills_Retinanet import detect_object

os.path.join(os.getcwd(), 'Documents/Repos/proj-SWATKINS-HWY_Camera_Classification/ETL')


def main():
    # Make an dataframe that will end up holding the experience buffer:
    outputData = pd.DataFrame(columns=['CarId','Time','Coords','Grid-Box'])
   
    timestamp = outputData.copy()
    time_df= outputData.copy()
    time_df = time_df['Time']
    loc_df = outputData.copy()
 
    locs = loc_df[['Time','Coords','CarId']].copy()
    locs = locs.set_index('CarId')
    speeds = []
    for dex in locs.index.unique():
        locations = locs.loc[dex]
        vel = speed(locations)
        locations['pixelSpeed'] = vel
        locations['speed mph'] = vel/30
       
        for p in range(len(locations)):
            speeds.append(vel/30)    
    timestamp['Speed'] = speeds  
​
  
    myBuffer0 = priorized_experience_buffer()
    episodeBuffer0 = priorized_experience_buffer()
   
    for d in range(ranger-2):    
        start_range = dates.index[d]
        end_range = dates.index[d+1]
        foo = get_date_range(timestamp, start_range, end_range)
        state = get_grid_matrix(foo)
​
        start_next = dates.index[d+1]
        end_next = dates.index[d+2]
        next_state = get_date_range(timestamp,start_next,end_next)
        next_state = get_grid_matrix(next_state)
        action = random.randint(0,9)
        reward = 0
        d = 'FALSE'
        legal_a_one = 0
        legal_a_one_s1 = 0
​
        #entry = {"state":[state], 'action':[action], 'reward':[reward],'s1:':[next_state], 'd':[d], 'legal_a_one':[legal_a_one], 'legal_a_one_s1':[legal_a_one_s1]}
        #experience_buffer= experience_buffer.append(entry, ignore_index=True)
        episodeBuffer0.add(np.reshape(np.array([state,action,reward,next_state,d,legal_a_one, legal_a_one_s1]),[1,7]))
        #exp_buff.add(experience)
        #print("experience:",episodeBuffer0)
    myBuffer0.add(episodeBuffer0.buffer)
​
    #print("smaple of 20:")
    #print(myBuffer0.buffer[1])
    return myBuffer0.buffer
   

​
​
def get_date_range(output_df,start_range, end_range): 
        out = output_df
        start_hour = start_range.hour 
        start_minute = start_range.minute 
        start_second = start_range.second
        start_mili = start_range.microsecond
        cat = str(start_hour) + ':' + str(start_minute)+ ':' + str(start_second) + "."+str(start_mili)
        #print("start of range:" ,cat)
        end_hour = end_range.hour
        end_minute = end_range.minute
        end_second = end_range.second 
        end_mili=end_range.microsecond 
        cat2 = str(end_hour)+":"+str(end_minute)+":"+str(end_second) + "." +str(end_mili)
        #print("end of range:",cat2)
​
        partition = out.between_time(*pd.to_datetime([cat,cat2]).time)
        return partition
​
def get_grid_matrix(output_df):
    p_state = np.zeros((8,13,2))
    valid_spots = [
        (0,2),
        (0,3),
        (1,2),
        (1,3),
        (2,2),
        (2,3),
        (3,0),
        (3,1),
        (3,2),
        (3,3),
        (3,4),
        (3,5),
        (3,6),
        (3,7),
        (3,8),
        (3,9),
        (3,10),
        (4,0),
        (4,1),
        (4,2),
        (4,3),
        (4,4),
        (4,5),
        (4,6),
        (4,7),
        (4,8),
        (5,0),
        (5,1),
        (5,2),
        (5,3),
        (5,4),
        (5,5),
        (5,6),
        (6,2),
        (6,3),
        (7,2),
        (7,3)
    ]
​
    for p in range(len(output_df)):
        box = output_df['Grid-Box'][p]
        if box != None:
            #print("box:",box)
            x = int(box[1])
            #print("x:",x)
            y = int(box[3:-1])
            #print("y:",y)
​
            p_state[x,y]= [1,int(round(spd))]
    return p_state
​
​
​
​
if __name__ == "__main__":
    batch_size = 20
    foo = main()
    print(foo[1])
​
    
    csv_buffer = '/home/krouse/school/filled_buffer.csv'
​
​
​
    writer = csv.writer(open(csv_buffer, 'w'))
    for row in foo:
         writer.writerow(row)