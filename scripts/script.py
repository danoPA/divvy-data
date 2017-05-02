import sqlite3 as sql
import pandas as pd
import numpy as np

from math import radians, cos, sin, asin, sqrt

pd.set_option('display.width', 1500)

def haversine(row):
    # convert decimal degrees to radians     
    #convert lon, lat to floats
    row['FROM LONGITUDE'], row['FROM LATITUDE'], row['TO LONGITUDE'], row['TO LATITUDE'] = \
          map(float, [row['FROM LONGITUDE'], row['FROM LATITUDE'], row['TO LONGITUDE'], row['TO LATITUDE']])
    lon1, lat1, lon2, lat2 = \
          map(radians, [row['FROM LONGITUDE'], row['FROM LATITUDE'], row['TO LONGITUDE'], row['TO LATITUDE']])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    
    c = 2 * asin(sqrt(a))    
    r = 3956  # Radius of earth in kilometers. Use 3956 for miles 6371km for miles
    
    return c * r

CONN = sql.connect("/Users/divya/projects/pandas/divvy-example/Divvy_Trips.db")

#df = pd.read_sql("SELECT [FROM STATION NAME], count(*)"\
#       "FROM temp GROUP BY [FROM STATION NAME]", con = CONN)

#strsql = "SELECT [TRIP ID], (abs([FROM LONGITUDE] - [TO LONGITUDE]) * abs([FROM LONGITUDE] - [TO LONGITUDE]))" \
#        " + (abs([FROM LATITUDE]-[TO LATITUDE]) * abs([FROM LONGITUDE] - [TO LONGITUDE])) AS DISTANCE FROM temp"

#strsql = "SELECT [START TIME], [STOP TIME] FROM temp"

#df = pd.read_sql(stations, con = CONN)
#print df.dtypes

#df["START TIME"] = pd.to_datetime(df["START TIME"], format="%m/%d/%Y %I:%M:%S %p")
#df["STOP TIME"] = pd.to_datetime(df["STOP TIME"], format="%m/%d/%Y %I:%M:%S %p")
#print df.dtypes

#print df.head()
stations = "SELECT * FROM temp WHERE [FROM STATION ID] = 90 OR [TO STATION ID] = 90";
df = pd.read_sql(stations, con = CONN)

# ADD NEW COLUMN TO DATAFRAME (RUN AGGREGATES ON THIS - SUM/MEAN/MEDIAN/STD)
df['DISTANCE_KM'] = df.apply(haversine, axis=1)

print df.head()

CONN.close()

