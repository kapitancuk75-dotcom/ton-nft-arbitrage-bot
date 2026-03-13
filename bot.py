import asyncio
import os

from aiogram import Bot, Dispatcher
from markets import get_getgems, get_portals
from arbitrage import find_arbitrage

TOKEN = os.getenv("BOT_TOKEN")
chat_id_env = os.getenv("CHAT_ID")

if chat_id_env is None:
    raise Exception("CHAT_ID не найден в переменных Railway")

CHAT_ID = int(chat_id_env)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def scanner():

    while True:

        try:

            getgems = await get_getgems()
            portals = await get_portals()

            deals = find_arbitrage(getgems, portals)

            for deal in deals:

                text = f"""
🔥 NFT Арбитраж

NFT: {deal['name']}

Buy: {deal['buy']} TON
Sell: {deal['sell']} TON

Profit: {deal['profit']} TON
"""

                await bot.send_message(CHAT_ID, text)

        except Exception as e:

            print("ERROR:", e)

        await asyncio.sleep(60)


async def main():

    asyncio.create_task(scanner())

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
