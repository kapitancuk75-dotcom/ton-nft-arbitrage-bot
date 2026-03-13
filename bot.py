import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from markets import get_getgems, get_portals
from arbitrage import find_arbitrage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not CHAT_ID:
    raise ValueError("CHAT_ID is not set")

CHAT_ID = int(CHAT_ID)


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 60))


async def scanner():

    logger.info("Scanner started")

    while True:

        try:

            logger.info("Fetching marketplaces...")

            getgems = await get_getgems()
            portals = await get_portals()

            deals = find_arbitrage(getgems, portals)

            if not deals:
                logger.info("No arbitrage found")

            for deal in deals:

                text = (
                    f"🔥 <b>NFT Арбитраж</b>\n\n"
                    f"<b>NFT:</b> {deal['name']}\n\n"
                    f"<b>Buy:</b> {deal['buy']} TON\n"
                    f"<b>Sell:</b> {deal['sell']} TON\n\n"
                    f"<b>Profit:</b> {deal['profit']} TON"
                )

                await bot.send_message(CHAT_ID, text)

            logger.info("Scan completed")

        except Exception as e:
            logger.exception("Scanner error")

        await asyncio.sleep(SCAN_INTERVAL)


async def on_startup():

    logger.info("Bot started")

    asyncio.create_task(scanner())


async def on_shutdown():

    logger.info("Bot shutting down")
    await bot.session.close()


async def main():

    try:

        await on_startup()
        await dp.start_polling(bot)

    finally:

        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
