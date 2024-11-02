# script for fetching daily updates of pokemon product cards
import requests
import json
from datetime import datetime
from time import sleep
from db import storeSalesData, storeProductData
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
    while(True):
        try:

            response = requests.request("POST", url, headers=headers, proxies=getRandomProxy(),data=payload)
            break
        except Exception as e:
            print(e)
            sleep(randint(3,5))

    return response.json()

def getProductListings(product_id):
    url = f"https://mp-search-api.tcgplayer.com/v1/product/{product_id}/listings?mpfev=2759"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://www.tcgplayer.com",
        "priority": "u=1, i",
        "referer": "https://www.tcgplayer.com/",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    data = {
        "filters": {
            "term": {
                "sellerStatus": "Live",
                "channelId": 0,
                "language": ["English"],
                "condition": ["Near Mint"]
            },
            "range": {
                "quantity": {
                    "gte": 1
                }
            },
            "exclude": {
                "channelExclusion": 0
            }
        },
        "from": 0,
        "size": 10,
        "sort": {
            "field": "price+shipping",
            "order": "asc"
        },
        "context": {
            "shippingCountry": "US",
            "cart": {}
        },
        "aggregations": ["listingType"]
    }

    response = requests.post(url, headers=headers, json=data)

    print(response.json())

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
    while(True):
        try:

            response = requests.request("GET", url, headers=headers, proxies=getRandomProxy(), data=payload)
            break
        except Exception as e:
            print(e)
            sleep(randint(3,5))
    return response.json()


def saveProducts(pokeman_cards):
    for card in pokeman_cards:
        product_id = card['productId']
        cardName = card['productName']
        if('japanese' in cardName.lower()):
            continue
        product_data = getProductByID(int(product_id),periods[3])
        sleep(randint(3,5))
        for sku in product_data['result']:
            if(sku['condition'] == 'Near Mint' and sku['language'] != 'Japanese'):
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
                listings = getProductListings(int(product_id))
                listingCount = 0
                if listings != None:
                    for listing in listings['results'][0]['results']:
                        title = listing['customData']['title']
                        if('japanese' in  title.lower()):
                            continue
                        listingCount += 1
                storeProductData(data, listingCount)
        # if(product_data):
        #     storeProductData(product_data)
        # sleep(randint(40,60))

# product = getProductByID(product_id,periods[3])

def getPokemonCards(start,end):
    size = 24
    offset = start
    while(offset <= end):
        print(f'fetching {offset} to {offset+size}')
        nextResult = getAllPokemanCards(offset, size)
        saveProducts(nextResult['results'][0]['results'])
        offset += size

def getAllPokeman():
    print('fetching cards')
    firstResult = getAllPokemanCards(0)
    total_results = firstResult['results'][0]['totalResults']
    # total_results = 27424
    print(f'total {total_results}')
    saveProducts(firstResult['results'][0]['results'])
    # temp block for testing
    threads = []
    for i in range(THREADS_COUNT):
        start = int(total_results/24/THREADS_COUNT)*i
        end = int(total_results/24/THREADS_COUNT)*(i+1)
        end = end if end < total_results else total_results
        thread = threading.Thread(target=getPokemonCards,args=(start,end))
        threads.append(thread)

    for thread in threads:
            thread.start()

    for thread in threads:
        thread.join()
    
    return 


getAllPokeman()