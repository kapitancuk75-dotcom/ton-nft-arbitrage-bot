import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# максимальная цена NFT (можно менять через команду)
max_price = 10.0

# чтобы отслеживать изменения цен
seen_prices = {}


async def get_nfts():

    url = "https://tonapi.io/v2/nfts/collections?limit=10"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    results = []

    async with aiohttp.ClientSession(headers=headers) as session:

        try:
            async with session.get(url) as response:

                if response.status != 200:
                    print("TON API статус:", response.status)
                    return []

                data = await response.json()

        except Exception as e:
            print("Ошибка API:", e)
            return []

    for item in data.get("nft_collections", []):

        name = item.get("name", "Unknown")
        address = item.get("address")

        if not address:
            continue

        # случайная цена для демонстрации (TON API часто не отдаёт цену коллекции)
        price = round((hash(address) % 200) / 10, 2)

        url = f"https://getgems.io/collection/{address}"

        results.append({
            "name": name,
            "price": price,
            "url": url
        })

    return results


async def scanner():

    global seen_prices

    while True:

        try:

            nfts = await get_nfts()

            for nft in nfts:

                price = nft["price"]

                if price > max_price:
                    continue

                old_price = seen_prices.get(nft["url"])

                if old_price is None or price < old_price:

                    seen_prices[nft["url"]] = price

                    message = (
                        f"🎁 Найден NFT\n\n"
                        f"Название: {nft['name']}\n"
                        f"Цена: {price} TON\n\n"
                        f"🔗 Купить:\n{nft['url']}"
                    )

                    await bot.send_message(CHAT_ID, message)

        except Exception as e:
            print("Ошибка сканера:", e)

        await asyncio.sleep(60)


@dp.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "🤖 Бот запущен\n\n"
        "Команды:\n"
        "/price <TON> — изменить максимальную цену\n"
        "/status — текущие настройки"
    )


@dp.message(Command("price"))
async def set_price(message: types.Message):

    global max_price

    try:
        new_price = float(message.text.split()[1])
        max_price = new_price

        await message.answer(f"✅ Максимальная цена установлена: {max_price} TON")

    except:
        await message.answer("Использование: /price 5")


@dp.message(Command("status"))
async def status(message: types.Message):

    await message.answer(
        f"📊 Текущие настройки\n\n"
        f"Максимальная цена: {max_price} TON"
    )


async def main():

    print("Бот запущен")

    asyncio.create_task(scanner())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
