import os
import sqlite3 as sql
import pandas as pd
import numpy as np
from finalDivvyAnalysis import divvy_create_graph


CONN = sql.connect("/Users/divya/projects/pandas/divvy-example/Divvy_Trips.db")
cur = CONN.cursor()
cur.execute("SELECT DISTINCT [FROM STATION ID], [FROM STATION NAME] FROM temp WHERE [FROM STATION ID] IN('596', '90', '304', '75', '345')") #create a list of tuples


weatherData = pd.read_csv("/Users/divya/projects/pandas/divvy-example/weatherByData.csv").set_index(['Month'], drop=True)

for row in cur.fetchall():
    divvy_create_graph(row[0], row[1], weatherData)

cur.close()
CONN.close()
