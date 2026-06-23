import json

categories = {
    "Flower": "花",
    "Glass": "ガラス",
    "Beverage": "飲み物",
    "Light": "光",
    "Memory": "記憶",
    "Remains": "遺骸",
    "Wood": "木材",
    "Egg": "卵",
    "Instrument": "楽器",
    "Liquid": "液体",
    "Metal": "金属",
    "Fabric and Fibre": "布と繊維",
    "Leaf": "葉",
    "Living Relic": "生きた遺物"
}

with open('data/item_requirements.json', 'r', encoding='utf-8') as f:
    item_reqs = json.load(f)

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# build a reverse map of en -> ja for items
en_to_ja = {}
for item in data['items']:
    en_to_ja[item['name_en']] = item['name_ja']

# Add some hardcoded ones if missing
en_to_ja["Solomon’s Preparation"] = "ソロモンの調合"
en_to_ja["Wire (Orichalcum)"] = "針金（オリハルコン）"
en_to_ja["Wire (Silver)"] = "針金（銀）"

def translate_req(req):
    if req in categories:
        return categories[req]
    if req in en_to_ja:
        return en_to_ja[req]
    return req

for item in data['items']:
    en_name = item.get('name_en')
    if en_name in item_reqs:
        req = item_reqs[en_name]
        if req == "-":
            continue
            
        trans_req = translate_req(req)
        
        # Check if we already added it
        already_added = False
        for htg in item.get('how_to_get', []):
            if "必須素材:" in htg:
                already_added = True
                
        if not already_added:
            if 'how_to_get' not in item:
                item['how_to_get'] = []
            item['how_to_get'].append(f"必須素材: {trans_req}")

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Added required items to how_to_get in items.json")
