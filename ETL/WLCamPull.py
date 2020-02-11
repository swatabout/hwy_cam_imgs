import requests
import json
from pandas import read_json
from pandas.io.json import json_normalize
from math import cos, degrees 
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy as sql
import pyodbc
import sys
import numpy as np

#SQL and WL API credentials

#sql connection, query and df
query =engine.execute('''SELECT [left], [right], [top], [bottom] FROM warehouse.dbo.geo_us_grid''')
table = pd.DataFrame(query.fetchall(), columns=query.keys())

#choose only North American coordinates
subset=table.loc[(table["right"].between(-130, -75)&table["left"].between(-130, -75)&table['top'].between(23,50)&table['bottom'].between(23,50))]

# camlist = pd.DataFrame(columns = ['acknowledgement', 'cameraLatitude','cameraLongitude','cameraProvince','name','snapshotUrl','sslAvailable','videoUrl'])                               

camlist = []
for row in range(len(table)):
    try: 
        response = requests.get("https://api.weatherlogics.com/traffic/camera?type=type=bbox&bbox=%d,%d,%d,%d" % (table['bottom'][row],table['left'][row],table['top'][row],table['right'][row]), 
                        headers = headers, 
                        params = params)
        raw = response.json()
        print(response.content)
    except requests.exceptions.RequestException as e: 
        raw = None
        if response.status_code == 200:
            print(response)
        else:
            pass

    # append json to dataframe
    if raw is not None and raw.get('cameras') is not None:
        loads = json.loads(json.dumps(raw))['cameras']
        camlist.extend(loads) 
        

camlist.append(loads.acknowledgement,loads.cameraLatitude,loads.cameraLongitude,loads.cameraProvince,loads.name,loads.snapshotUrl,loads.sslAvailable,loads.videoUrl)

#transform json to df to put into sql table
df = pd.DataFrame(camlist, columns = ['acknowledgement', 'cameraLatitude','cameraLongitude','cameraProvince','name','snapshotUrl','sslAvailable','videoUrl'])
dictdf = pd.DataFrame.from_dict(loads).reset_index()
tempdf = pd.DataFrame.from_dict(json.loads(json.dumps(raw))).reset_index()
camlist= pd.concat([camlist, dictdf])

cams = pd.DataFrame.from_dict(camlist)
cams.columns = ['acknowledgement','lat','long','State', 'Intersection', 'Image URL','sslAvailable','videoURL']      

#drop unnecessary columns
cams = cams.drop(columns = ['acknowledgement', 'sslAvailable', 'videoURL'])

#push to sql 
#cams.to_sql(name="StateTrafficCameras", con=engine, if_exists="append")
