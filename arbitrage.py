MIN_PROFIT = 3


def find_arbitrage(getgems, portals):

    profitable = []

    for nft in getgems:

        name = nft["name"]
        buy_price = nft["price"]

        if name in portals:

            sell_price = portals[name]

            profit = sell_price - buy_price

            if profit >= MIN_PROFIT:

                profitable.append({
                    "name": name,
                    "buy": buy_price,
                    "sell": sell_price,
                    "profit": profit
                })

    return profitable
