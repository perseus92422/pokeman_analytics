print("test")
val ={'results':[]}

try:
    result = val['result']
    print(result)
except KeyError:
    print("exception",val)
