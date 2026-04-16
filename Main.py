import asyncio

import json

import os

import discord

from Vinted import get_items

 

# Chargement config

with open('config.json', 'r') as f:

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

                   # Construction embed Discord

                   embed = discord.Embed(

                       title=item.get('title', 'Sans titre'),

                       url=item.get('url', ''),

                       color=0x09B1BA

                   )

                   price = item.get('price', {}).get('amount', '?')

                   currency = item.get('price', {}).get('currency_code', 'EUR')

                   embed.add_field(name='Prix', value=f'{price} {currency}', inline=True)

                   embed.add_field(name='Recherche', value=search['query'], inline=True)

                   # Photo

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
