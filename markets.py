import aiohttp

async def get_getgems():

    url = "https://api.getgems.io/graphql"

    query = {
        "query": """
        {
          nfts(first:40){
            edges{
              node{
                name
                address
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

        if price:

            nfts.append({
                "name": name,
                "price": float(price) / 1e9
            })

    return nfts


async def get_portals():

    url = "https://portals.market/api"

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as r:

            data = await r.json()

    prices = {}

    for nft in data:

        prices[nft["name"]] = nft["price"]

    return prices
