import requests
import sqlalchemy as sql
from datetime import datetime
import pandas as pd
import pyodbc
import os 
import boto3
import io

Server = "freightwaves.ctaqnedkuefm.us-east-2.rds.amazonaws.com"
Database = "Warehouse"
#PWD = os.environ['sqlpass']
#UID = os.environ['sqluid']

#aws credintials
Username = 'FW-bucket-user'
Access_key_ID = 'AKIAI675MCFO5KZMA7CQ'
Secret_Access_Key = '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'

# Connect to SQL
conn = pyodbc.connect('Driver={SQL Server}; Server=freightwaves.ctaqnedkuefm.us-east-2.rds.amazonaws.com;Database=Warehouse; uid=fwdbmain; pwd=7AC?Ls9_z3W#@XrR')

# Create queries that pull information we need during loops
each_state = f"SELECT UUID, [Image URL], State FROM Warehouse.dbo.StateTrafficCameras"
unique_states_list = "SELECT DISTINCT([State]) FROM Warehouse.dbo.StateTrafficCameras"

# Grab all states in table and create list of states
states_df=pd.read_sql(unique_states_list, conn)
states = []
for i in states_df.State:
    states.append(i)

# Pull all information for each state to add into s3 bucket directories
each_state_df = pd.read_sql(each_state, conn)
each_state_df[each_state_df[['Image URL','State'] 'State' == 'GA']]
GA = each_state_df[(each_state_df['State']=='GA')]
1

# Start s3 session
session = boto3.Session(Access_key_ID, Secret_Access_Key) 
s3 = session.resource('s3')
bucketname='statictrafficcameras'

# Create s3 directories of all States used in SQL
s3_client = boto3.client('s3')
for state in states:
    response = s3_client.put_object(Bucket=bucketname,Key=f'{state}/')

for i in range(len(df)):
    today = datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")
    img_name = f"{df['UUID'][i]}_{today}.png"
    url=df['Image_URL'][i]
    r=requests.get(url, stream=True)
    img_bytes = io.BytesIO(r.content)
    img_obj = s3.Object(bucketname, img_name)
    img_obj.put(Body=img_bytes)
    if i % 25 == 0:
        print(f'{i} finished')
        
        
df['UUID'][0]
datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")



# Create s3 bucket 'folder'
s3.









