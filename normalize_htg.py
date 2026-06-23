import json

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

replacements = {
    "海辺 / Sea's Edge で1ペニーを捨てる": "海辺で1ペニーを捨てる",
    "海辺でペニーを捨てる": "海辺で1ペニーを捨てる",
    "井戸 / Well に1ペニーを捨てる": "井戸に1ペニーを投げる",
    "井戸にペニーを投げる": "井戸に1ペニーを投げる",
    "海辺で何かを捨てる": "海辺で何かを捨てる", # This is fine
}

for item in data['items']:
    if 'how_to_get' in item:
        new_htg = []
        for htg in item['how_to_get']:
            replaced = replacements.get(htg, htg)
            new_htg.append(replaced)
        
        # Remove duplicates
        seen = set()
        dedup = []
        for x in new_htg:
            if x not in seen:
                seen.add(x)
                dedup.append(x)
        item['how_to_get'] = dedup

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Normalization complete.")
