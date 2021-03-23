import requests
from bs4 import BeautifulSoup
import sqlite3

count = 1

conn = sqlite3.connect('tenders.db',timeout=60*60)
conn.execute('''CREATE TABLE IF NOT EXISTS TENDERS_DATA (ID INTEGER PRIMARY KEY AUTOINCREMENT, TENDER_NO TEXT, CITY TEXT, \
     ORGANIZATION TEXT, TYPE TEXT, WORK TEXT, WORK_CODE TEXT, TENDER_LINK TEXT, ADVERTISED_DATE TEXT, CLOSING_DATE TEXT, \
     CLOSING_TIME TEXT);''')

while True:
    url = "https://www.ppra.org.pk/dad_tenders.asp?PageNo=" + str (count)
    count+=1
    r = requests.get(url)
    print(count)
    
    if r.ok and count<94:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find_all("table")

        for i in range(1,len(table[4].find_all('tr'))):
            row = table[4].find_all('tr')[i]

            tender_no = row.find_all('td')[0].p.string.strip()
            organization_and_country = row.find_all('td')[1].find('font').find_all('br')[0].previousSibling.string.strip().split(",")
            organization = organization_and_country[0]
            city = organization_and_country[1][1:]
            tender_type = row.find_all('td')[1].find('font').find_all('br')[0].nextSibling.string.strip()
            work = row.find_all('td')[1].find('font').find_all('br')[1].nextSibling.string.strip()
            work_code = row.find_all('td')[1].find('font').find_all('br')[2].nextSibling.string.strip()
            tender_link = "https://www.ppra.org.pk/"+row.find_all('td')[2].find('a').get('href').strip()
            advertised_date = row.find_all('td')[3].find('font').string.strip()
            closing_date = row.find_all('td')[4].find('font').find_all('br')[0].previousSibling.string.strip()
            closing_time = row.find_all('td')[4].find('font').find_all('br')[0].nextSibling.string.strip()

            conn.execute("INSERT INTO TENDERS_DATA (TENDER_NO, CITY, ORGANIZATION, TYPE, WORK, WORK_CODE, TENDER_LINK, ADVERTISED_DATE, CLOSING_DATE, CLOSING_TIME) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(tender_no,city,organization,tender_type,work,work_code,tender_link,advertised_date,closing_date,closing_time))
    elif count==94:
        break

conn.commit()
conn.close()