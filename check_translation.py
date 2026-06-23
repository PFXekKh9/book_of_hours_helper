import json
import re

with open('data/items.json', 'r') as f:
    data = json.load(f)

untranslated_names = 0
english_in_how_to_get = 0

for item in data['items']:
    if item['name_ja'] == item['name_en']:
        untranslated_names += 1
    
    for htg in item.get('how_to_get', []):
        if re.match(r'^[a-zA-Z0-9\s\'\,\.]+$', htg):
            english_in_how_to_get += 1

print(f"Untranslated names: {untranslated_names}")
print(f"English in how_to_get: {english_in_how_to_get}")
