import os
import asyncio
import aiohttp
from aiogram import Bot

# переменные среды
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise Exception("BOT_TOKEN не найден")

if not CHAT_ID:
    raise Exception("CHAT_ID не найден")

CHAT_ID = int(CHAT_ID)

bot = Bot(token=TOKEN)

MIN_PROFIT = 3


async def get_getgems():

    url = "https://api.getgems.io/graphql"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://getgems.io",
        "Referer": "https://getgems.io/"
    }

    query = {
        "query": """
        {
          nfts(first: 20) {
            edges {
              node {
                name
                sale {
                  price
                }
              }
            }
          }
        }
        """
    }

    nfts = []

    async with aiohttp.ClientSession(headers=headers) as session:

        try:

            async with session.post(url, json=query) as response:

                # защита от CloudFront HTML
                if response.content_type != "application/json":
                    text = await response.text()
                    print("Getgems вернул HTML:", text[:200])
                    return []

                data = await response.json()

        except Exception as e:

            print("Ошибка запроса Getgems:", e)
            return []

    try:

        for item in data["data"]["nfts"]["edges"]:

            node = item["node"]

            name = node.get("name")

            sale = node.get("sale")

            if not sale:
                continue

            price = sale.get("price")

            if not price:
                continue

            price = float(price) / 1e9

            nfts.append({
                "name": name,
                "price": price
            })

    except Exception as e:

        print("Ошибка обработки данных:", e)

    return nfts


async def scan_market():

    while True:

        try:

            nfts = await get_getgems()

            for nft in nfts:

                buy_price = nft["price"]

                sell_price = buy_price * 1.5

                profit = sell_price - buy_price

                if profit >= MIN_PROFIT:

                    message = f"""
🔥 Найден NFT

Название: {nft['name']}

Цена покупки: {buy_price:.2f} TON
Цена продажи: {sell_price:.2f} TON

Прибыль: {profit:.2f} TON
"""

                    await bot.send_message(CHAT_ID, message)

        except Exception as e:

            print("Ошибка сканирования:", e)

        await asyncio.sleep(60)


async def main():

    print("Бот запущен")

    await scan_market()


if __name__ == "__main__":
    asyncio.run(main())
