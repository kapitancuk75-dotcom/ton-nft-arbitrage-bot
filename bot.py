import aiohttp
import asyncio
import os

from aiogram import Bot, Dispatcher
from markets import get_getgems, get_portals
from arbitrage import find_arbitrage

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

MIN_PROFIT = 3


async def get_getgems():

    url = "https://api.getgems.io/graphql"

    query = {
        "query": """
        {
          nfts(first:30){
            edges{
              node{
                name
                sale{
                  price
                }
              }
            }
          }
        }
        """
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(url, json=query) as r:

            text = await response.text()
print(text)

nfts = []

for nft in data["data"]["nfts"]["edges"]:

        name = nft["node"]["name"]
        price = nft["node"]["sale"]["price"]

        nfts.append({
            "name": name,
            "price": float(price)/1e9
        })

    return nfts


async def scan():

    while True:

        try:

            nfts = await get_getgems()

            for nft in nfts:

                buy = nft["price"]
                sell = buy * 1.5

                profit = sell - buy

                if profit >= MIN_PROFIT:

                    msg = f"""
NFT: {nft["name"]}

Buy: {buy} TON
Sell: {sell} TON

Profit: {profit} TON
"""

                    await bot.send_message(CHAT_ID, msg)

        except Exception as e:
            print(e)

        await asyncio.sleep(30)


async def main():

    asyncio.create_task(scan())

    await dp.start_polling(bot)


asyncio.run(main())
