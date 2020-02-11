import requests
from multiprocessing import Pool
from datetime import datetime
import numpy
import pandas as pd
import pyodbc
import sqlalchemy as sql
from time import time
import boto3
import io
import psutil

#pd.options.display.max_columns = 999
#pd.options.display.max_rows = 999

# Connect to SQL
# conn = pyodbc.connect(f'Driver=ODBC Driver 17 for SQL Server; Server={Server};Database={Database}; uid=fwdbmain; pwd=7AC?Ls9_z3W#@XrR')
engine = sql.create_engine(f'mssql+pymssql://{UID}:{PWD}@{Server}/{Database}')
conn = engine.connect()


# Create queries that pull information we need during loops
# Also define states within query so that we don't query the whole thing yets ############CHANGE THIS WHEN WE MOVE TO BITQUERY#############################
cam_qual_per_state = "SELECT t1.[Image.URL],t1.[UUID],t2.[CameraQuality],t1.[State] FROM [Warehouse].[dbo].[statetrafficcamera_temp] t2 LEFT JOIN Warehouse.dbo.StateTrafficCameras t1 ON t1.UUID = t2.UUID WHERE t2.CameraQuality = '1' and t1.state in ('TN', 'GA')"


#  Create DF of of Images,UUID, and the 38 states we are using. This will be used to loop through to add pictures to bucket every 15 minutes.
all_states_df = pd.read_sql(cam_qual_per_state, conn)
print(all_states_df)
all_urls = []
for url in all_states_df['Image.URL'].tolist():
    all_urls.append(url)
uuids = []
for uuid in all_states_df['UUID']:
    uuids.append(uuid)
values = all_states_df.values.tolist()
    
# List of all states with quality images
# states = ['AZ', 'BC', 'CA', 'CO', 'CT', 'FL', 'GA', 'IA', 'ID', 'IN', 'KS', 'KY', 'LA', 'MA', 'ME', 'MI', 'MN', 'MO', 'MX', 'MT', 'NB', 'NC', 'ND', 'NE', 'NH', 'NM', 'NY', 'OH', 'ON', 'OR', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WY']
#states = ['TN', 'GA']

"""                                                     /////---NOT USING ALL STATES DUE TO HOW LONG IT TAKES TO RUN---\\\\ 
# Pull all information for each state to add into s3 bucket directories
each_states_df = pd.read_sql(each_state, conn)
each_states_df.dropna(inplace=True)
GA = each_states_df[(each_states_df['State']==f'{i}')]
"""

# Should be finished with SQL Database. Close connection
conn.close()

# Start s3 session
session = boto3.Session(Access_key_ID, Secret_Access_Key) 
print(session)
s3 = session.resource('s3')
print(s3)
bucketname='statictrafficcameras'

def get_imgs(value):
    try:
        today = datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")
        url = value[0]
        uuid = value[1]
        state = value[3]
        img_name = f'{uuid}_{today}.png'
        r=requests.get(url, stream=True)
        if r.status_code==200:
            img_bytes = io.BytesIO(r.content)
            img_obj = s3.Object(bucketname, f'{state}/'+img_name)
            img_obj.put(Body=img_bytes)
            print(f"{uuid}:{url} finished.")
        elif r.status_code != 200:
            print(f'{url} has a bad status_code')
            return None
        else:
            return None
    except:
         print(f'URL: \n {url} is rejecting request...')
         return None

#end()
#print(f'{end()-start()/60} minutes to complete process.')

if __name__ == '__main__':

    # Measure memory usage
    process = psutil.Process()

    start = time()
    p = Pool(15)
    p.map(get_imgs, values)
    r = p.map_async(get_imgs, values)
    r.wait()
    p.terminate()
    p.join()
    end = time()
    memory = process.memory_info().rss / 1e6
    print(f'{(end-start)} seconds to complete process.')
    print(f'Memory Usage : {(memory)}') #bytes
"""-----------------------END OF WORKING SCRIPT-----------------------------"""

"""count = 0   
avg_time_list = []
start = time.time()
for i in states_df.values:
    state = i[3]
    if state in i[1]:
        if count < 2000:
            try:
                start_loop = time.time()
                today = datetime.now().strftime("%Y-%m-%d_%Hh:%Mm")
                img_name = f"{i[1]}_{today}.png"
                url=all_urls[count]
                r=requests.get(url, stream=True)
                if r.status_code == 200:
                    img_bytes = io.BytesIO(r.content)
                    img_obj = s3.Object(bucketname, f'{state}/'+img_name)
                    img_obj.put(Body=img_bytes)
                    print(f'{url} finished')
                    count += 1
                elif r.status_code != 200:
                    print(f'{url} has a bad status_code')
                    continue
                else:
                    print('Not sure what is happening here')
            except:
                 print(f'URL: \n {url} is rejecting request. Starting next loop...')
                 continue
            end_loop = time.time()
            avg_time_list.append(end_loop-start_loop)
        else:
            print('Reached 2000 Images. Loop ended.')
            break
    else:
        continue
end = time.time()
print(f'{(end-start)/60} minutes to complete process.')
print(f'{np.mean(avg_time_list)} average seconds per iteration.')"""


"""-------------------END OF CURRENT SQL QUERY FOR 5 STATES-----------------------"""
"""t1.State IN ('OR','CT','GA','WA','FL')"""
