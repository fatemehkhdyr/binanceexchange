from sys import stdout
from rejson import Client, Path
from timeloop import Timeloop
from datetime import timedelta, datetime
from decouple import config
import aiohttp
import asyncio
import os

proxies = os.getenv("HTTP_PROXY") or ""
cache_host = config("CACHE_ADDRESS")
cache_port = config("CACHE_PORT")

client = Client(host=cache_host, port=cache_port, db=0, decode_responses=True)
loop = asyncio.get_event_loop()


async def get_binance_exchangerate():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://www.binance.com/api/v3/ticker/price",
                proxy=proxies,
                timeout=6,
            ) as exchangerates:
                if exchangerates.status != 200:
                    return "problem with binance api and errorcode is {}".format(
                        exchangerates.status
                    )
                exchangerates = await exchangerates.json()
                result = {"rates": {}, "updated_time": None}
                for exchangerate in exchangerates:
                    result["rates"][exchangerate["symbol"]] = float(
                        exchangerate["price"]
                    )
                current_time = datetime.now().timestamp()
                result["updated_time"] = current_time
                return result
        except Exception as e:
            stdout.write("Exception happend in update coin price :\n" + str(e) + "\n")
            stdout.flush()
            return None


async def get_binance_coin_asset_list():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.binance.com/api/v3/exchangeInfo", proxy = proxies) as info:
                if info.status != 200:
                    return "problem with binance api and errorcode is {}".format(
                        info.status
                    )
                info = await info.json()
                coin_asset = set()
                for coin in info["symbols"]:
                    coin_asset.add(coin["baseAsset"])
                coins_list =list(coin_asset)
                data = {"coin_list":sorted(coins_list)}
                return data
        except Exception as e:
            stdout.write("Exception happend in asset list update :\n" + str(e) + "\n")
            stdout.flush()
            return None



def update_redis_coin_price():
    data = loop.run_until_complete(get_binance_exchangerate())
    if data:
        client.jsonset("exchangerate", Path.rootPath(), data)
        stdout.write(
            "updated coin price in "
            + str(
                datetime.fromtimestamp(
                    client.jsonget("exchangerate", Path(".updated_time"))
                ).strftime("/%Y/%m/%d, %H:%M:%S")
                + "\n"
            )
        )
        stdout.flush()


def update_redis_coin_list():
    data = loop.run_until_complete(get_binance_coin_asset_list())
    if data:
        client.jsonset('coin_list', Path.rootPath(), data)
        stdout.write(
            "updated coin assets list in  "
            + str(
                datetime.now()
            )+ "\n"
        )
        stdout.flush()

tl = Timeloop()


@tl.job(interval=timedelta(seconds=8))
def updater():
    update_redis_coin_price()

@tl.job(interval=timedelta(seconds=14))
def coin_list_updater():
    update_redis_coin_list()


update_redis_coin_list()
update_redis_coin_price()
tl.start(block=True)
