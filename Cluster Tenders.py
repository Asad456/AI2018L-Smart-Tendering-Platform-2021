import pandas as pd
import sqlite3
from kmodes.kmodes import KModes

#Craete connection to database
conn = sqlite3.connect('tenders.db',timeout=60)

#Read all tenders from table TENDERS_DATA as pandas dataframe
original_data = pd.read_sql_query("SELECT * FROM TENDERS_DATA",conn)

#Read all tenders from table TENDERS_DATA as pandas dataframe for temporarily use
temp_data = pd.read_sql_query("SELECT * FROM TENDERS_DATA",conn)

#Drop columns which we does not take interest now.
temp_data = temp_data.drop(['ID','TENDER_NO','CITY','WORK_CODE','TENDER_LINK','ADVERTISED_DATE','CLOSING_DATE','CLOSING_TIME'],axis=1)

#Make array of tenders details from pandas dataframe for KMODES algorithm which cluster the tenders
mark_array = temp_data.values

#Apply KMODES algorithm for clustering
kmode = KModes(n_clusters=30, init='Huang', n_init=5, verbose=1)
#Get cluster numbers of tenders

clusters = kmode.fit_predict(mark_array)

print(clusters)
#Take cluster numbers in a list
cluster_list=[]
for c in clusters:
    cluster_list.append(c)

print(cluster_list)

#Merger cluster numbers list with original dataframe
original_data['CLUSTER']=cluster_list

#Create table CLUSTER_DATA to store user clustered tenders
conn.execute('''DROP TABLE IF EXISTS CLUSTER_DATA''')
original_data.to_sql('CLUSTER_DATA', conn, if_exists='replace', index=False)
conn.commit()

#Close database connection
conn.close()
