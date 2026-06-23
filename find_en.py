import json
import re

with open('data/items.json', 'r') as f:
    data = json.load(f)

for item in data['items']:
    if item['name_ja'] == item['name_en']:
        print(f"NAME: {item['name_en']}")
    
    for htg in item.get('how_to_get', []):
        if re.match(r'^[a-zA-Z0-9\s\'\,\.]+$', htg):
            print(f"HTG [{item['name_ja']}]: {htg}")
