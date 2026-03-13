import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher

# Получаем переменные окружения
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if TOKEN is None:
    raise Exception("BOT_TOKEN не найден")

if CHAT_ID is None:
    raise Exception("CHAT_ID не найден")

CHAT_ID = int(CHAT_ID)

bot = Bot(token=TOKEN)
dp = Dispatcher()

MIN_PROFIT = 3


async def get_getgems():

    url = "https://api.getgems.io/graphql"

    query = {
        "query": """
        {
          nfts(first:40){
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

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    nfts = []

    async with aiohttp.ClientSession() as session:

        async with session.post(url, json=query, headers=headers) as response:

            # если API вернул не JSON
            if response.content_type != "application/json":
                text = await response.text()
                print("Getgems вернул не JSON:", text)
                return []

            data = await response.json()

    try:

        for nft in data["data"]["nfts"]["edges"]:

            node = nft["node"]

            name = node["name"]

            sale = node.get("sale")

            if sale is None:
                continue

            price = sale.get("price")

            if price is None:
                continue

            price = float(price) / 1e9

            nfts.append({
                "name": name,
                "price": price
            })

    except Exception as e:
        print("Ошибка обработки NFT:", e)

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
🔥 Найден арбитраж

NFT: {nft['name']}

Купить: {buy_price:.2f} TON
Продать: {sell_price:.2f} TON

Прибыль: {profit:.2f} TON
"""

                    await bot.send_message(CHAT_ID, message)

        except Exception as e:

            print("Ошибка сканирования:", e)

        await asyncio.sleep(60)


async def main():

    print("Бот запущен")

    asyncio.create_task(scan_market())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
