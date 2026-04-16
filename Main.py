import asyncio
import json
import os
import discord
import httpx

BASE_URL = 'https://www.vinted.fr/api/v2/catalog/items'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
    'Accept': 'application/json',
}

async def get_items(query, max_price=None, size=None):
    params = {
        'search_text': query,
        'order': 'newest_first',
        'per_page': 20,
    }
    if max_price:
        params['price_to'] = max_price
    if size:
        params['size_id[]'] = size
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        try:
            r = await client.get(BASE_URL, params=params)
            if r.status_code == 200:
                return r.json().get('items', [])
        except Exception as e:
            print(f'Erreur API Vinted: {e}')
    return []

with open('Config.json', 'r') as f:
    config = json.load(f)

TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

seen_ids = set()

async def monitor():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    print(f'Bot démarré. Surveillance sur {len(config["searches"])} recherche(s).')

    while not client.is_closed():
        for search in config['searches']:
            items = await get_items(
                search['query'],
                search.get('max_price'),
                search.get('size', '')
            )
            for item in items:
                item_id = item.get('id')
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    embed = discord.Embed(
                        title=item.get('title', 'Sans titre'),
                        url=item.get('url', ''),
                        color=0x09B1BA
                    )
                    price = item.get('price', {}).get('amount', '?')
                    currency = item.get('price', {}).get('currency_code', 'EUR')
                    embed.add_field(name='Prix', value=f'{price} {currency}', inline=True)
                    embed.add_field(name='Recherche', value=search['query'], inline=True)
                    photos = item.get('photos', [])
                    if photos:
                        embed.set_thumbnail(url=photos[0].get('url', ''))
                    await channel.send(embed=embed)
        await asyncio.sleep(config.get('poll_interval', 30))

@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user}')
    client.loop.create_task(monitor())

client.run(TOKEN)
