import requests
import json
from datetime import datetime
from time import sleep
from random import randint
from db import storeSalesData, storeProductData
from time import sleep
from random import randint
product_line_id = 3 # pokeman product 
product_id = 560405 # test one
periods = ['month','quarter','semi-anuual','annual']


def getAllPokemanCards(start,size=24):
    url = "https://mp-search-api.tcgplayer.com/v1/search/request?q=&isList=false&mpfev=2725"

    payload = json.dumps({
    "algorithm": "sales_synonym_v2",
    "from": start,
    "size": size,
    "filters": {
        "term": {
        "productLineName": [
            "pokemon"
        ]
        },
        "range": {},
        "match": {}
    },
    "listingSearch": {
        "context": {
        "cart": {}
        },
        "filters": {
        "term": {
            "sellerStatus": "Live",
            "channelId": 0,
            "printing": [
            "Holofoil"
            ],
            # "condition": [
            # "Near Mint"
            # ]
        },
        "range": {
            "quantity": {
            "gte": 1
            }
        },
        "exclude": {
            "channelExclusion": 0
        }
        }
    },
    "context": {
        "cart": {},
        "shippingCountry": "US",
        "userProfile": {}
    },
    "settings": {
        "useFuzzySearch": True,
        "didYouMean": {}
    },
    "sort": {}
    })
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.tcgplayer.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tcgplayer.com/',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()



def getProductByID(product_id,period):
    url = f'https://infinite-api.tcgplayer.com/price/history/{product_id}/detailed?range={period}'
    payload={}
    headers = {
    'accept': '/',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://www.tcgplayer.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tcgplayer.com/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    #   'x-pagerequest-id': '1724889838216:www.tcgplayer.com/product/560405/pokemon-sv-shrouded-fable-cassiopeia-094-064'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()

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

def getAllSalesData(product_id, mpfev=2698):
    offest = 0
    limit = 25
    product_id = int(product_id)
    first_sales_data = getLatestSalesByID(product_id,offest,limit,mpfev)
    if('japanese' in first_sales_data['data'][0]['title'].lower()):
        return []
    total_count = first_sales_data['totalResults']
    sales_data = first_sales_data['data']
    offest += limit
    while offest < total_count:
        partial_data = getLatestSalesByID(product_id, offest, limit, mpfev)
        sales_data += partial_data['data']
        offest += limit
        sleep(randint(15,30))
    return sales_data
        
def getAllPokeman():
    print('fetching cards')
    # firstResult = getAllPokemanCards(0)
    # total_results = firstResult['results'][0]['totalResults']
    total_results = 27424
    print(f'total {total_results}')
    size = 24
    # offset  = size
    offset = 48
    # saveProducts(firstResult['results'][0]['results'])
    # temp block for testing
    while(offset <= total_results):
        print(f'fetching {offset} to {offset+size}')
        nextResult = getAllPokemanCards(offset, size)
        try:
            saveProducts(nextResult['results'][0]['results'])
            offset += size
        except KeyError:
            print("Exception KeyError:",nextResult)
            break
    return 

def fetchAllSalesData():
    pokeman_cards = getAllPokeman()
    for card in pokeman_cards:
        product_id = card['productId']
        sales_data = getAllSalesData(product_id)
        if(len(sales_data) > 0):
            storeSalesData(sales_data)
        sleep(randint(40,60))

# fetchAllSalesData()


def saveProducts(pokeman_cards):
    for card in pokeman_cards:
        product_id = card['productId']
        cardName = card['productName']
        if('japanese' in cardName.lower()):
            continue
        product_data = getProductByID(int(product_id),periods[3])
        sleep(randint(3,5))
        for sku in product_data['result']:
            if(sku['condition'] == 'Near Mint' and sku['variant'] == 'Holofoil' and sku['language'] != 'Japanese'):
                data = {
                    'productId' : product_id,
                    'title' : cardName,
                    'trending' : sku['trendingMarketPricePercentages'],
                    'buckets' : json.dumps(sku['buckets']),
                    'skuId' : sku['skuId'],
                    'totalQuantitySold' : sku['totalQuantitySold'],
                    'totalTransactionCount' : sku['totalTransactionCount'],
                    'averageDailyQuantitySold' : sku['averageDailyQuantitySold'],
                    'averageDailyTransactionCount' : sku['averageDailyTransactionCount']
                }
                storeProductData(data, 0)
        # if(product_data):
        #     storeProductData(product_data)
        # sleep(randint(40,60))

# product = getProductByID(product_id,periods[3])

getAllPokeman()