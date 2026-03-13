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


async def get_collections():

    url = "https://tonapi.io/v2/nfts/collections?limit=10"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    collections = []

    async with aiohttp.ClientSession(headers=headers) as session:

        try:
            async with session.get(url) as response:

                if response.status != 200:
                    print("TON API статус:", response.status)
                    return []

                data = await response.json()

        except Exception as e:
            print("Ошибка запроса:", e)
            return []

    try:

        for item in data.get("nft_collections", []):

            name = item.get("name", "Unknown collection")
            address = item.get("address")

            if not address:
                continue

            # ссылка на маркетплейс
            url = f"https://getgems.io/collection/{address}"

            collections.append({
                "name": name,
                "url": url
            })

    except Exception as e:
        print("Ошибка обработки данных:", e)

    return collections


async def scanner():

    while True:

        try:

            collections = await get_collections()

            for col in collections:

                message = (
                    f"📦 NFT коллекция\n\n"
                    f"Название: {col['name']}\n\n"
                    f"🔗 Открыть:\n{col['url']}"
                )

                await bot.send_message(
                    CHAT_ID,
                    message,
                    disable_web_page_preview=False
                )

        except Exception as e:
            print("Ошибка сканера:", e)

        await asyncio.sleep(120)


async def main():

    print("Бот запущен")

    await scanner()


if __name__ == "__main__":
    asyncio.run(main())
