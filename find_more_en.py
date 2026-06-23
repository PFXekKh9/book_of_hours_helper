import json
import re

with open('data/items.json', 'r') as f:
    data = json.load(f)

for item in data['items']:
    for htg in item.get('how_to_get', []):
        # If the string does not contain any Japanese characters (Hiragana, Katakana, Kanji)
        if not re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', htg):
            # Ignore plain numbers or empty strings
            if re.search(r'[a-zA-Z]', htg):
                print(htg)
