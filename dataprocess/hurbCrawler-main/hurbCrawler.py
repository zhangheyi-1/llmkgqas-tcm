import csv
import time

import requests
from bs4 import BeautifulSoup
import getEachPages

import random

def get_headers():
    # 随机获取一个headers
    user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
                   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
                   ]
    headers = {'User-Agent':random.choice(user_agents)}
    return headers
def get_new_csv(path='medicineTable.csv'):
    return open(path, 'w', newline="", encoding='utf-8-sig')
for page in range(10012644, 10034001):
# for page in range(10001001, 10001003):
    dbEntry = []
    page_url = 'https://db.yaozh.com/fangji/'+ str(page) + '.html'
    res = requests.get(page_url, headers=get_headers())
    res.encoding = 'UTF-8'
    soup = BeautifulSoup(res.text, 'lxml')
    # body > div.main > div.body.detail - main > div.table - wrapper > table > tbody > tr: nth - child(1) > th
    # / html / body / div[7] / div[2] / div[1] / table / tbody / tr[1] / th
    try:
        medicines = soup.find('table', {'class': 'table'}).find_all('tr')
        for medicine in medicines:
            tr = medicine.text.split()
            dbEntry.append({tr[0]:tr[1]})
    except AttributeError as e:
        print('Error!', e)
        continue
    print(dbEntry)
    with open("medicineTable.csv",'a+',encoding='utf-8',newline='') as fp:
        csv_write = csv.writer(fp)
        csv_write.writerow(dbEntry)
    time.sleep(random.choice([1,2,3]))


