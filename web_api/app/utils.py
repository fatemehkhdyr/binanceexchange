from rejson import Client, Path
from datetime import datetime
from decouple import config


cache_address = config("CACHE_ADDRESS")
port= config("CACHE_PORT")

client = Client(host=cache_address, port=port,db=0,decode_responses=True)

def seprate_pairs(pairs):
    coin_asset = client.jsonget('coin_list', Path(".coin_list"))
    pair_list=[]
    for i in range(len(pairs)):
        if pairs[:i+1] in coin_asset and pairs[i+1:] in coin_asset:
            pair_list += [pairs[:i+1], pairs[i+1:]]
            return pair_list
    return pair_list

def get_undefine_exchangerate_from_cache(coin):
    first_coin = coin[0] + 'USDT'
    second_coin = coin[1] + 'USDT'
    if first_coin in client.jsonobjkeys('exchangerate', Path('.rates')) and second_coin in client.jsonobjkeys('exchangerate', Path('.rates')):
        first_coin_rate = client.jsonget('exchangerate', Path(".rates."+first_coin))
        second_coin_rate = client.jsonget('exchangerate', Path(".rates."+second_coin))
        rate = first_coin_rate/second_coin_rate
        return rate
    return "this pair is not define in binance"

def get_exchangerate(pairs):
    coin = seprate_pairs(pairs)
    if len(coin)!=2:
        return "The size of input is wrong"
    coin_name = coin[0]+coin[1]
    if coin_name in client.jsonobjkeys('exchangerate', Path('.rates')):
        return client.jsonget('exchangerate', Path(".rates."+coin_name))
    return get_undefine_exchangerate_from_cache(coin)

def get_all_coin_exchangerate_from_cache():
    response = client.jsonget('exchangerate', Path('.rates'))
    return response

def services_healthy():
    current_timestamp = int(datetime.now().timestamp())
    updated_time = client.jsonget('exchangerate', Path('.updated_time'))
    if current_timestamp - updated_time < 10:
        return True, updated_time
    return False, updated_time
