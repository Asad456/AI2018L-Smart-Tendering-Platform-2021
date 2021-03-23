import pandas as pd
import sqlite3
from kmodes.kmodes import KModes

def myFunc(e):
  return e[2]

#Creating list of user clicks on tenders with parameters tender_id, user_id and no_of_clicks
user_history = [["TS446135E",'USER1',5],["TS446129E",'USER1',9],["TS446107E",'USER1',2]]  

#Sort list based on no of clicks in descending order
user_history.sort(reverse=True, key=myFunc)  

#Craete connection to database
conn = sqlite3.connect('tenders.db',timeout=60*60)

#Below code read cluster no of tenders which user clicks
clusters = set()
for item in user_history:
    cur = conn.cursor()
    cur.execute("SELECT CLUSTER FROM CLUSTER_DATA WHERE TENDER_NO=?",(item[0],))
    cluster = cur.fetchall()[0][0]
    clusters.add(cluster)

#Below code read tenders from table CLUSTER_DATA based on above cluster no of tenders which user clicks as pandas dataframe
data_frames_list = []
for cluster in clusters:
    data = pd.read_sql_query("SELECT * FROM CLUSTER_DATA WHERE CLUSTER=" + str(cluster),conn)
    data_frames_list.append(data)

#Concatenate dataframe list to single data frame which we later use after clustering again tenders based on user given work interest
original_data = pd.concat(data_frames_list, ignore_index=True)

#Concatenate dataframe list to single data frame for temporarily use
temp_data_frame = pd.concat(data_frames_list, ignore_index=True)

#Drop columns which we does not take interest now. We use only CITY, TYPE and WORK of tender columns because we take only these parameters from user for work interest
temp_data_frame = temp_data_frame.drop(['ID','TENDER_NO','WORK_CODE','ORGANIZATION','TENDER_LINK','ADVERTISED_DATE','CLOSING_DATE','CLOSING_TIME','CLUSTER'],axis=1)

#Take temporary data for user work interest based on CITY, TYPE and WORK of tenders
user_data = pd.DataFrame({'CITY':["Karachi"],'TYPE':["Miscellaneous Items"],'WORK':["Supply of Mobile Receipt Printers"]})

#Concatenate user work interest data in last row of tenders data in which user clicks
final_data_frame = pd.concat([temp_data_frame,user_data], ignore_index = True)

#Make array of tenders details from pandas dataframe for KMODES algorithm which cluster the some tenders with user work interest row
mark_array = final_data_frame.values

#Apply KMODES algorithm for clustering
kmode = KModes(n_clusters=10, init='Huang', n_init=5, verbose=1)
#Get cluster numbers of tenders
clusters = kmode.fit_predict(mark_array)

#Take cluster numbers in a list
cluster_list=[]
for c in clusters:
    cluster_list.append(c)

#Get user work interest row cluster no
user_cluster_no = cluster_list[len(cluster_list)-1]
#Delete user work interest row cluster no from clusters_list list
cluster_list.pop(len(cluster_list)-1)

#Drop CLUSTER column from original tenders dataframe which we created above for tenders in which user clicks
original_data = original_data.drop(['CLUSTER'],axis=1)

#Merger cluster numbers list which we calculated after adding user work interset row to original dataframe
original_data['CLUSTER']=cluster_list

#Get those tenders which cluster with user work interest row and this is the recommended tenders for particular user
final_data = original_data[original_data['CLUSTER']== user_cluster_no]

#Create table USER_DATA to store user recommended tenders
conn.execute('''DROP TABLE IF EXISTS USER_DATA''')
final_data.to_sql('USER_DATA', conn, if_exists='replace', index=False)
conn.commit()

#Close database connection
conn.close()

