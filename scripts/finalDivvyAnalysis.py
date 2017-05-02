import os
import sqlite3 as sql
import pandas as pd
import numpy as np
import calendar as cal
import datetime as dt
import wes

from math import radians, cos, sin, asin, sqrt
from matplotlib import rc, pyplot as plt
from functools import reduce

def divvy_create_graph(station_id, station_name, weather):

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
        r = 3956  # Radius of earth in kilometers. Use 3956 for miles 6371km for km
        
        return c * r
    
    font = {'family' : 'arial', 'weight' : 'bold', 'size'   : 15}
    rc('font', **font); rc("figure", facecolor="white"); rc('axes', edgecolor='darkgray');

    def runplot(pvtdf, title, path):        
        pvtdf.plot(kind='bar', edgecolor='w',figsize=(20,5), width=0.5, fontsize = 10)
        locs, labels = plt.xticks()    
        plt.title(title, weight='bold', size=24)
        lgd = plt.legend(loc='right', ncol=14, frameon=True, shadow=False, prop={'size': 12}, bbox_to_anchor=(1, 0.95))
        for i in range(len(lgd.get_texts())): 
            text = lgd.get_texts()[i].get_text().replace('(DISTANCE_Miles, ', '(')
            lgd.get_texts()[i].set_text(text)
        plt.xlabel('Year', weight='bold', size=24)
        plt.ylabel('Distance', weight='bold', size=20)
        plt.tick_params(axis='x', bottom='off', top='off', labelsize=15)
        plt.tick_params(axis='y', left='off', right='off', labelsize=15)
        plt.grid(b=True)
        plt.setp(labels, rotation=0, rotation_mode="anchor", ha="center")
        plt.tight_layout()
        plt.savefig(path)

    def htmlpage(datastring, title, filename):
        html = '''<!DOCTYPE html>
                  <html>
                      <head>
                         <style type="text/css">
                              body{{ 
                                      margin:15px; padding: 20px 100px 20px 100px;
                                      font-family:Arial, Helvetica, sans-serif; font-size:88%; 
                              }}
                              h1, h2 {{
                                      font:Arial black; color: #383838;
                                      valign: top;
                              }}       
                              img {{
                                    float: right;
                              }}
                              table{{
                                      width:100%; font-size:13px;                  
                                      border-collapse:collapse;
                                      text-align: right;                  
                              }}
                              th{{ color: #383838 ; padding:2px; text-align:right; }}
                              td{{ padding: 2px 5px 2px 5px; }}
                              .footer{{
                                      text-align: right;
                                      color: #A8A8A8;
                                      font-size: 12px;
                                      margin: 5px;
                              }}                   
                         </style>
                      </head>                      
                      <body>
                        <h3>{0}<img src="../../divvylogo.svg" alt="divvy icon" height="50px"></h3>
                        {1}
                      </body>
                      <div class="footer">Source: City of Chicago Data Portal</div>
                  </html>'''.format(title, datastring)
        with open(os.path.join(cd, 'stations', station_name, filename), 'w') as f: 
            f.write(html)

    CONN = sql.connect("/Users/divya/projects/pandas/divvy-example/Divvy_Trips.db")
    stations = "SELECT * FROM temp WHERE [FROM STATION ID] = {0} OR [TO STATION ID] = {0}".format(station_id);
    df = pd.read_sql(stations, con = CONN)
    CONN.close()

    # create folder
    cd = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(cd, 'stations', station_name)) == False:
        os.makedirs(os.path.join(cd, 'stations', station_name))

    #NEW COLUMNS
    df['DISTANCE_Miles'] = df.apply(haversine, axis=1)
    df["START TIME"] = pd.to_datetime(df["START TIME"], format="%m/%d/%Y %I:%M:%S %p")
    df["STOP TIME"] = pd.to_datetime(df["STOP TIME"], format="%m/%d/%Y %I:%M:%S %p")
    
    df.loc[:, 'TRIP DURATION'] = df['TRIP DURATION'].astype(float)/60

    df.loc[:, 'START TIME MONTH'] = df['START TIME'].dt.month
    df.loc[:, 'START TIME YEAR'] = df['START TIME'].dt.year
    df.loc[:, 'STOP TIME MONTH'] = df['STOP TIME'].dt.month
    df.loc[:, 'STOP TIME YEAR'] = df['STOP TIME'].dt.year
    df.loc[:, 'START WEEKDAY'] = [cal.day_name[i] for i in df['START TIME'].dt.weekday]

    df['BIRTH YEAR'] = np.where(df["BIRTH YEAR"] == '', np.nan, df["BIRTH YEAR"])
    df['BIRTH YEAR'] = df['BIRTH YEAR'].astype('float')
    df.loc[:, 'AGE'] = df['START TIME YEAR'] - df['BIRTH YEAR']

    df['AGE_GROUP'] = np.where(df['AGE'].between(0,18, inclusive = True), '0 - 18',
                          np.where(df['AGE'].between(19,29, inclusive = True), '19 - 29',
                              np.where(df['AGE'].between(30,39, inclusive = True), '30 - 39',
                                  np.where(df['AGE'].between(40,49, inclusive = True), '40 - 49',
                                      np.where(df['AGE'].between(50,65, inclusive = True), '50 - 65',
                                          np.where(df['AGE'].between(65,80, inclusive = True), '65+', np.nan))))))

    df.loc[:, 'START TIME HOUR'] = df['START TIME'].dt.hour
    df['TIME FRAME'] = np.where(df['START TIME HOUR'].between(0,1, inclusive = True), '00:00-01:00',
                           np.where(df['START TIME HOUR'].between(1,2, inclusive = True), '01:00-02:00',
                               np.where(df['START TIME HOUR'].between(2,3, inclusive = True), '02:00-03:00',
                                   np.where(df['START TIME HOUR'].between(3,4, inclusive = True), '03:00-04:00',
                                       np.where(df['START TIME HOUR'].between(4,5, inclusive = True), '04:00-05:00',
                                           np.where(df['START TIME HOUR'].between(5,6, inclusive = True), '05:00-06:00',
                                           np.where(df['START TIME HOUR'].between(6,7, inclusive = True), '06:00-07:00',
                                               np.where(df['START TIME HOUR'].between(7,8, inclusive = True), '07:00-08:00',
                                                   np.where(df['START TIME HOUR'].between(8,9, inclusive = True), '08:00-09:00',
                                                       np.where(df['START TIME HOUR'].between(9,10, inclusive = True), '09:00-10:00', 
                                                           np.where(df['START TIME HOUR'].between(10,11, inclusive = True), '10:00-11:00',
                                                               np.where(df['START TIME HOUR'].between(11,12, inclusive = True), '11:00-12:00',
                                                                   np.where(df['START TIME HOUR'].between(12,13, inclusive = True), '12:00-13:00', 
                                                                       np.where(df['START TIME HOUR'].between(13,14, inclusive = True), '13:00-14:00', 
                                                                           np.where(df['START TIME HOUR'].between(14,15, inclusive = True), '14:00-15:00', 
                                                                               np.where(df['START TIME HOUR'].between(15,16, inclusive = True), '15:00-16:00', 
                                                                                   np.where(df['START TIME HOUR'].between(16,17, inclusive = True), '16:00-17:00', 
                                                                                       np.where(df['START TIME HOUR'].between(17,18, inclusive = True), '17:00-18:00', 
                                                                                           np.where(df['START TIME HOUR'].between(18,19, inclusive = True), '18:00-19:00', 
                                                                                               np.where(df['START TIME HOUR'].between(19,20, inclusive = True), '19:00-20:00', 
                                                                                                   np.where(df['START TIME HOUR'].between(20,21, inclusive = True), '20:00-21:00', 
                                                                                                       np.where(df['START TIME HOUR'].between(21,22, inclusive = True), '21:00-22:00', 
                                                                                                           np.where(df['START TIME HOUR'].between(22,23, inclusive = True), '22:00-23:00', 
                                                                                                               np.where(df['START TIME HOUR'].between(23,24, inclusive = True), '23:00-24:00', np.nan)))))))))))))))))))))))) 

    #overall
    df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].count().reset_index().to_csv(os.path.join(cd, 'stations', station_name, 'tripCount.csv'))
    htmlpage(df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].count().reset_index().to_html(), '{} - Trip Count'.format(station_name), 'TripCount.html')
    #df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].count().reset_index().to_html(os.path.join(cd, 'stations', station_name, 'tripCount.html'))
    df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].mean().reset_index().to_csv(os.path.join(cd, 'stations', station_name, 'averageDuration.csv'))
    #df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].mean().reset_index().to_html(os.path.join(cd, 'stations', station_name, 'averageDuration.html'))
    htmlpage(df.groupby(['START TIME YEAR', 'START TIME MONTH'])['TRIP DURATION'].mean().reset_index().to_html(), '{} - Trip Duration'.format(station_name), 'AvgDuration.html')
    df.groupby(['START TIME YEAR', 'START TIME MONTH'])['DISTANCE_Miles'].mean().reset_index().to_csv(os.path.join(cd, 'stations', station_name, 'averageDistance.csv'))
    htmlpage(df.groupby(['START TIME YEAR', 'START TIME MONTH'])['DISTANCE_Miles'].mean().reset_index().to_html(), '{} - Avg Miles'.format(station_name), 'AvgDistance.html')
    #df.groupby(['START TIME YEAR', 'START TIME MONTH'])['DISTANCE_Miles'].mean().reset_index().to_html(os.path.join(cd, 'stations', station_name, 'averageDistance.html'))

    #distance by gender
    distanceByGender = pd.pivot_table(df[(df['USER TYPE'] == 'Subscriber') & (df['GENDER'] != '')], index=['START TIME YEAR', 'START TIME MONTH'], columns=['GENDER'], values=['DISTANCE_Miles'], aggfunc=len)
    distanceByGender.plot(title= "{} - Distance in miles by gender".format(station_name), figsize=(20,5))
    lgd = plt.legend()
    for i in range(len(lgd.get_texts())): 
        text = lgd.get_texts()[i].get_text().replace('(DISTANCE_Miles, ', '(')
        lgd.get_texts()[i].set_text(text)
    plt.savefig(os.path.join(cd, 'stations', station_name, 'distanceByGender.png'))

    miles_by_gender = pd.pivot_table(df[(df['USER TYPE'] == 'Subscriber') 
            & (df["AGE"] < 80) & (df["GENDER"].str.len() > 0)
            & (df["DISTANCE_Miles"] > 0)], index = ['START TIME YEAR'], 
        columns=['GENDER'], values=['DISTANCE_Miles'], aggfunc = len)

    miles_by_gender.reset_index().to_csv(os.path.join(cd, 'stations', station_name, 'milesByGender.csv'))
    htmlpage(miles_by_gender.reset_index().to_html(), '{} - Miles By Gender'.format(station_name), 'MilesByGender.html')
    #miles_by_gender.reset_index().to_html(os.path.join(cd, 'stations', station_name, 'milesByGender.html'))

    wes.set_palette('FantasticFox')    
    runplot(miles_by_gender,' {} - Divvy Data subscribers, distance by age and gender'.format(station_name), os.path.join(cd, 'stations', station_name, 'milesByGender.png'))

    mergelist = []

    for yr in list(range(df['START TIME YEAR'].min(), df['START TIME YEAR'].max() + 1)):
        miles_by_gender_pie = None
        miles_by_gender_pie = df[(df['USER TYPE'] == 'Subscriber') & (df['START TIME YEAR']==yr) & (df["GENDER"].str.len() > 0)].\
            groupby(["GENDER", "START TIME YEAR"])["DISTANCE_Miles"].apply(len).reset_index()
        
        mergelist.append(miles_by_gender_pie[['GENDER', 'DISTANCE_Miles']])
    
    miles_by_gender_pie = reduce(lambda left,right: pd.merge(left, right, on='GENDER'), mergelist)    
    miles_by_gender_pie.columns = ['GENDER'] + [str(i) for i in list(range(df['START TIME YEAR'].min(), df['START TIME YEAR'].max() + 1))]

    labels = 'Female', 'Male'
    #pie = plt.pie(miles_by_gender_pie, labels=labels)
    miles_by_gender_pie.plot.pie(subplots=True, labels=['', ''], figsize=(12,3.8), autopct='%.2f')
    plt.axis('equal')
    plt.legend(labels=labels)
    plt.savefig(os.path.join(cd, 'stations', station_name, 'milesByGenderPIE.png'))

    #Customer v Subscriber
    user_type_pie = df.groupby(["START TIME YEAR","USER TYPE"]).apply(len).reset_index()
    user_type_pie.columns = ['Year', 'User Type', 'People']

    customervsubscriber = pd.pivot_table(user_type_pie, index=['User Type'], columns=['Year'], values=['People'])
    labels = ['Customer', 'Subscriber']
    customervsubscriber.plot.pie(subplots=True, labels=['', ''], figsize=(12,3.8), autopct='%.2f')
    plt.axis('equal')
    plt.legend(labels=labels)
    plt.savefig(os.path.join(cd, 'stations', station_name, 'customervSubscriber.png'))
    
    #Miles by Age#
    miles_by_age = pd.pivot_table(df[(df['USER TYPE'] == 'Subscriber') 
            & (df["AGE"] < 80)
            & (df["GENDER"].str.len() > 0)
            & (df["DISTANCE_Miles"] > 0)], index = ['START TIME YEAR'], 
        columns=['AGE_GROUP'], values=['DISTANCE_Miles'], aggfunc = np.sum)

    runplot(miles_by_age, '{} - Divvy Data subscribers, total distance by age'.format(station_name), os.path.join(cd, 'stations', station_name, 'milesByAge.png'))
    htmlpage(miles_by_age.reset_index().to_html(), '{} - Miles By Age'.format(station_name), 'MilesByAge.html')

    #avDistanceByGender over Weather
    avDistanceMiles = pd.pivot_table(df[df['GENDER'] != ''] , 
                                        index=['START TIME MONTH'], columns=['GENDER'],
                                        values=['DISTANCE_Miles'], aggfunc=np.sum)
    total = avDistanceMiles.join(weather)

    DistancevsWeather = total.sort_values(['ATF'])
    DistancevsWeather["START TIME MONTH"] = DistancevsWeather.index.values
    DistancevsWeather = DistancevsWeather.set_index(['ATF'])

    line = DistancevsWeather[[0,1]].plot(title="Mean distance travelled by gender", figsize=(20,5))
    line.set_ylabel("Distance(miles)")
    line.set_xlabel("Time")
    lgd = plt.legend()
    for i in range(len(lgd.get_texts())): 
        text = lgd.get_texts()[i].get_text().replace('(DISTANCE_Miles, ', '(')
        lgd.get_texts()[i].set_text(text)
    plt.savefig(os.path.join(cd, 'stations', station_name, 'milesvsWeather.png'))
    htmlpage(DistancevsWeather.reset_index().to_html(), '{} - Distance vs Weather'.format(station_name), 'DistancevsWeather.html')
