import asyncio
import aiohttp
from aiogram import Bot, Dispatcher

TOKEN = "TOKEN_ТВОЕГО_БОТА"
CHAT_ID = 123456789

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

            data = await r.json()

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
