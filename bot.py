import os
import asyncio
import aiohttp
from aiogram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise Exception("BOT_TOKEN не найден")

if not CHAT_ID:
    raise Exception("CHAT_ID не найден")

CHAT_ID = int(CHAT_ID)

bot = Bot(token=TOKEN)

MIN_PROFIT = 3


async def get_nfts():

    url = "https://tonapi.io/v2/nfts?limit=20"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    nfts = []

    async with aiohttp.ClientSession(headers=headers) as session:

        try:

            async with session.get(url) as response:

                if response.status != 200:
                    print("Ошибка TON API:", response.status)
                    return []

                data = await response.json()

        except Exception as e:

            print("Ошибка запроса:", e)
            return []

    try:

        for nft in data.get("nft_items", []):

            name = nft.get("metadata", {}).get("name", "Unknown NFT")

            # примерная цена (TON API не всегда отдаёт цену)
            price = nft.get("sale", {}).get("price", 0)

            if not price:
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

            nfts = await get_nfts()

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
