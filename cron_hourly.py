# script for fetching all sales data of pokemon cards

import requests
import json
from datetime import datetime
from db import *
from time import sleep
from random import randint


def getLatestSalesByID(product_id, offset,limit, mpfev):
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

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def getAllSalesData(product_id,start, end, mpfev=2698):
    offest  = start
    limit = 25
    while offest < end:
        partial_data = getLatestSalesByID(product_id, offest, limit, mpfev)
        storeSalesData(partial_data['data'])
        offest += limit
        sleep(randint(2,3))
    return 


def getAllSalesData():
    products = getProductData()
    for product in products:
        offest = 0
        limit = 25
        product_id = int(product['productId'])
        first_sales_data = getLatestSalesByID(product_id,offest,limit,mpfev=2698)
        sales_data = first_sales_data['data']
        last_price = sales_data[0]['purchasePrice']
        
        latest_orderDate = getLatestOrderDate(product_id)
        while(True):
            new_data  =[]
            for item in sales_data:
                order_str = item['orderDate']
                if '.' in order_str:
                        # Format with fractional seconds
                    order_date_dt = datetime.strptime(order_str, "%Y-%m-%dT%H:%M:%S.%f+00:00")
                else:
                    # Format without fractional seconds
                    order_date_dt = datetime.strptime(order_str, "%Y-%m-%dT%H:%M:%S+00:00")
                if(order_date_dt > latest_orderDate):
                    item['productId'] = product_id
                    new_data.append(item)
            if(len(new_data) > 0):
                storeSalesData(new_data)
                offest += limit
                next_sales_data = getLatestSalesByID(product_id,offest,limit,mpfev=2698)
                sales_data = next_sales_data['data']
                sleep(randint(2,3))
            else:
                break
        print(product_id)
        open_price = getOpenPrice(product_id)
        open_price = last_price if open_price == None else open_price
        daily_drop = (last_price - open_price)/open_price
        updateProductData({'dailyDrop' : daily_drop, 'lastPrice' : last_price}, product_id) 


getAllSalesData()
