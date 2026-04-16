import httpx

import json

 

BASE_URL = 'https://www.vinted.fr/api/v2/catalog/items'

 

HEADERS = {

   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',

   'Accept': 'application/json',

}

 

async def get_items(query: str, max_price: float = None, size: str = None):

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

               data = r.json()

               return data.get('items', [])

       except Exception as e:

           print(f'Erreur API Vinted: {e}')

   return []
