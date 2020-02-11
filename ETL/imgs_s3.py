# Pull snapshots from urls and store images in s3 bucket

import requests, numpy, boto3, io, psutil
from multiprocessing import Pool
from datetime import datetime
import pandas as pd, sqlalchemy as sql
from time import time


# Connect to SQL
engine = sql.create_engine(f'mssql+pymssql://{UID}:{PWD}@{Server}/{Database}')
conn = engine.connect()


# Create queries that pull information we need during loops
cam_qual_per_state = "SELECT t1.[Image.URL],t1.[UUID],t2.[CameraQuality],t1.[State] FROM [Warehouse].[dbo].[statetrafficcamera_temp] t2 LEFT JOIN Warehouse.dbo.StateTrafficCameras t1 ON t1.UUID = t2.UUID WHERE t2.CameraQuality = '1' and t1.state in ('TN', 'GA')"


#  Create df of Images, UUID, and the states we are using 
all_states_df = pd.read_sql(cam_qual_per_state, conn)
print(all_states_df)
all_urls = []
for url in all_states_df['Image.URL'].tolist():
    all_urls.append(url)
uuids = []
for uuid in all_states_df['UUID']:
    uuids.append(uuid)
values = all_states_df.values.tolist()
    

# Close SQL connection
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
"""-----------------------END OF SCRIPT-----------------------------"""

