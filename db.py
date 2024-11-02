#module for store data into database
from pymongo import MongoClient
import json
from datetime import datetime, timedelta

def storeSalesData(data):
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    if('sales_data' not in userdb.list_collection_names()):
        collection = userdb.create_collection('sales_data')
    else:
        collection = userdb['sales_data']
    results = []
    for item in data:
        order_str = item['orderDate']
        if '.' in order_str:
                # Format with fractional seconds
            order_date_dt = datetime.strptime(order_str, "%Y-%m-%dT%H:%M:%S.%f+00:00")
        else:
            # Format without fractional seconds
            order_date_dt = datetime.strptime(order_str, "%Y-%m-%dT%H:%M:%S+00:00")
        data_with_date = item
        data_with_date['orderDate'] = order_date_dt
        results.append(data_with_date)
        
    result = collection.insert_many(results)
    myclient.close()
    return

def storeProductData(data,length):
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    if('products' not in userdb.list_collection_names()):
        collection = userdb.create_collection('products')
    else:
        collection = userdb['products']
    
    find_existing = collection.find_one({'skuId' : data['skuId']})
    today = datetime.now().date()
    if(find_existing == None):        
        listingCount = {str(today) : length}
        data['listingCount'] = json.dumps(listingCount)
        collection.insert_one(data)
    else:
        if('listingCount' in find_existing):
            #listingCount = json.loads(find_existing['listingCount'])
            listingCount = {}
            listingCount[str(today)] = length
            data['listingCount'] = json.dumps(listingCount)
            collection.update_one({'skuId' : data['skuId']},{'$set' : data})
        else:
            listingCount = {str(today) : length}
            data['listingCount'] = json.dumps(listingCount)
            collection.update_one({'skuId' : data['skuId']},{'$set' : data})


    myclient.close()
    return

def getProductData():
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    collection = userdb['products']
    result = collection.find()
    products = [doc for doc in result]
    return products


def getLatestOrderDate(product_id):
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    collection = userdb['sales_data']
    latest_order = collection.find_one(
        {'productId': product_id},   # Filter by product_id
        sort=[('orderDate', -1)]   # Sort by orderDate in descending order (-1)
    )
    return latest_order['orderDate']

def getOpenPrice(product_id):
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    collection = userdb['sales_data']
    today = datetime.now().date()
    today = datetime.combine(today, datetime.min.time())
    tmr = today + timedelta(days=1)
    first_order = collection.find_one(
        {'productId': product_id, 'orderDate' : {'$gte' : today, '$lt' : tmr} },   # Filter by product_id
        sort=[('orderDate', 1)]   # Sort by orderDate in descending order (-1)
    )
    if(first_order == None):
        return None
    else:
        return first_order['purchasePrice']

def updateProductData(data,product_id):
    myclient = MongoClient("mongodb://127.0.0.1:27017/")
    userdb = myclient["pokeman"]
    collection = userdb['products']
    collection.update_one({'productId' : product_id},{'$set' : data})
    return