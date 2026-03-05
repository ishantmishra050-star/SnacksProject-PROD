import urllib.request
import json
import urllib.parse

snacks = [
    "Bombay mix", "Bikaneri bhujia", "Chivda", "Khakhra", 
    "Mathri", "Bakarwadi", "Shankarpali", "Chakli", "Kachori", 
    "Khaja", "Thekua", "Pinni", "Ghevar", "Tilkut", "Anarsa", "Farsan"
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
        print(f"Failed for {snack}: {e}")

for k, v in images.items():
    print(f'"{k}": "{v}",')
