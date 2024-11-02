# script for fetching all sales data of pokemon cards

import requests
import json
from datetime import datetime
from time import sleep
from db import storeSalesData, getProductData
from time import sleep
from random import randint, choice
import threading

periods = ['month','quarter','semi-anuual','annual']

THREADS_COUNT = 30

def getRandomProxy():
    proxies_file = './proxy_seller.txt'
    with open(proxies_file,'r') as f:
        proxy_list = f.readlines()
        f.close()
    random_proxy = choice(proxy_list).strip()
    proxy = {
        'http' : 'socks5://' + random_proxy,
        'https' : 'socks5://' + random_proxy,
        }
    return proxy


def getLatestSalesByID(product_id, offset,limit, mpfev):
    print(f'fetching from {offset} to {offset + limit}')
    url = f"https://mpapi.tcgplayer.com/v2/product/{product_id}/latestsales?mpfev={mpfev}"
    timestamp_now = datetime.now().timestamp()

    payload = json.dumps({
        "conditions": [],
        "languages": [],
        "variants": [],
        "listingType": "All",
        "offset": offset,
        "limit": limit,
        "time": int(timestamp_now*1000)
    })
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.tcgplayer.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tcgplayer.com/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    while(True):
        try:

            response = requests.request("POST", url, proxies=getRandomProxy(), headers=headers, data=payload)
            break
        except Exception as e:
            print(e)
            sleep(randint(3,5))
    return response.json()


def getAllSalesDataById(product_id,start, end, mpfev=2698):
    offest  = start
    limit = 25
    while offest < end:
        partial_data = getLatestSalesByID(product_id, offest, limit, mpfev)
        data  = []
        for item in partial_data['data']:
            item['productId'] = product_id
            data.append(item)
        storeSalesData(data)
        offest += limit
        sleep(randint(2,3))
    return 


def getAllSalesData():
    products = getProductData()
    print('getting product data')
    for product in products:
        print(f'product id : {product["productId"]}')
        offest = 0
        limit = 25
        product_id = int(product['productId'])
        first_sales_data = getLatestSalesByID(product_id,offest,limit,mpfev=2698)
        total_count = first_sales_data['totalResults']
        sales_data = first_sales_data['data']
        data  = []
        for item in sales_data:
            item['productId'] = product_id
            data.append(item)
        storeSalesData(data)
        threads = []
        for i in range(THREADS_COUNT):
            start = int(total_count/24/THREADS_COUNT)*i
            end = int(total_count/24/THREADS_COUNT)*(i+1)
            end = end*24 if end*24 < total_count else total_count
            thread = threading.Thread(target=getAllSalesDataById,args=(product_id,start*24,end))
            threads.append(thread)
    
        for thread in threads:
                thread.start()

        for thread in threads:
            thread.join()
    
    return 


getAllSalesData()
