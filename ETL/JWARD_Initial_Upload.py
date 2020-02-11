import requests
from datetime import datetime
import pandas as pd
import pyodbc
import time
import boto3
import io

pd.options.display.max_columns = 999
pd.options.display.max_rows = 999

Server = "freightwaves.ctaqnedkuefm.us-east-2.rds.amazonaws.com"
Database = "Warehouse"
#PWD = os.environ['sqlpass']
#UID = os.environ['sqluid']

#aws credintials
Username = 'FW-bucket-user'
Access_key_ID = 'AKIAI675MCFO5KZMA7CQ'
Secret_Access_Key = '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'

# Connect to SQL
conn = pyodbc.connect(f'Driver=ODBC Driver 17 for SQL Server; Server={Server};Database={Database}; uid=fwdbmain; pwd=7AC?Ls9_z3W#@XrR')
                      
# Create queries that pull information we need during loops
each_state = f"SELECT UUID, [Image.URL], State FROM Warehouse.dbo.StateTrafficCameras"
unique_states_list = "SELECT DISTINCT([State]) FROM Warehouse.dbo.StateTrafficCameras"
cam_qual_per_state = "SELECT t1.[Image.URL],t1.[UUID],t2.[CameraQuality],t1.[State] FROM [Warehouse].[dbo].[statetrafficcamera_temp] t2 INNER JOIN Warehouse.dbo.StateTrafficCameras t1 ON t1.UUID = t2.UUID WHERE t2.CameraQuality = '1' AND t1.State IN ('FL','OR','WY','OH','TN')"

# Grab all states in table and create list of states
states_df=pd.read_sql(unique_states_list, conn)
states = []
for i in states_df.State:
    states.append(i)
    
# List of 5 States we are going to use for good camera quality images
five_states = ['FL','OR','WY','OH','TN']

#  Create DF of of Images,UUID, and the 5 states we are using. This will be used to loop through to add pictures to bucket every 15 minutes.
five_states_df = pd.read_sql(cam_qual_per_state, conn)


"""                                                      /////---NOT USING ALL STATES DUE TO HOW LONG IT TAKES TO RUN---\\\\\ 
# Pull all information for each state to add into s3 bucket directories
each_state_df = pd.read_sql(each_state, conn)
each_state_df.dropna(inplace=True)
GA = each_state_df[(each_state_df['State']==f'{i}')]
"""

# Start s3 session
session = boto3.Session(Access_key_ID, Secret_Access_Key) 
s3 = session.resource('s3')
bucketname='statictrafficcameras'

# Create s3 directories of all States used in SQL
"""                                                       //////---FINISHED---CAN ADD MORE IF MORE STATES ARE INSERTED INTO SQL---\\\\\\\
s3_client = boto3.client('s3')
for state in states:
    response = s3_client.put_object(Bucket=bucketname,Key=f'{state}/')
"""


"""                                                             /////---NOT USING ALL STATES DUE TO HOW LONG IT TAKES TO RUN---\\\\\
# Add all images for EVERY state into their specific directories
count = 0
for i in each_state_df.values:
    state = i[2]
    print(state)
    if state in i[0]:
        today = datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")
        img_name = f"{i[0]}_{today}.png"
        url=i[1]
        r=requests.get(url, stream=True)
        img_bytes = io.BytesIO(r.content)
        img_obj = s3.Object(bucketname, f'{state}/'+img_name)
        img_obj.put(Body=img_bytes)
        if count % 25 == 0:
            print(f'{count} finished')
        count += 1
        time.sleep(.2)
    else:
        pass
"""  
    
# Add all images for SPECIFIED FIVE STATES into their own directories in s3 bucket
count = 0
start = time.time()
for i in five_states_df.values:
    state = i[3]
    if state in i[1]:
        today = datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")
        img_name = f"{i[1]}_{today}.png"
        url=i[0]
        r=requests.get(url, stream=True)
        img_bytes = io.BytesIO(r.content)
        img_obj = s3.Object(bucketname, f'{state}/'+img_name)
        img_obj.put(Body=img_bytes)
        if count % 25 == 0:
            print(f'{count} finished')
        if count % 1870 == 0:
            time.sleep(1)
        count += 1
        time.sleep(.2)
    else:
        pass
end = time.time()
print(end-start)
        
        
