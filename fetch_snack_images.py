import urllib.request
import json
import urllib.parse

snacks = [
    "Khakhra", "Chakli", "Shankarpali", "Bhakarwadi", "Mathri", 
    "Bikaneri bhujia", "Poha", "Bombay mix", "Kachori", "Thekua", 
    "Pinni", "Tilkut", "Anarsa", "Khaja", "Farsan", "Chivda"
]

images = {}
for snack in snacks:
    encoded_snack = urllib.parse.quote(snack)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded_snack}&prop=pageimages&format=json&pithumbsize=600"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            for page_id in pages:
                if 'thumbnail' in pages[page_id]:
                    images[snack] = pages[page_id]['thumbnail']['source']
    except Exception as e:
        pass

import pprint
pprint.pprint(images)
