import json

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# First, remove any standalone "必須素材:" elements we added previously.
for item in data['items']:
    if 'how_to_get' in item:
        new_htg = []
        for htg in item['how_to_get']:
            if not htg.startswith("必須素材:"):
                new_htg.append(htg)
        item['how_to_get'] = new_htg

# Now, we need the requirements map again
# I can just rebuild it from the current data/item_requirements.json
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

translations = {
    "Mazarine Fife": "マザリン・ファイフ（楽器）",
    "Stymphling": "ステュンパロスの鳥",
    "Pyrus Auricalcinus": "ピルス・アウリカルキヌス",
    "Essential Periost": "骨膜のエッセンス",
    "Leathy": "レーテー",
    "Old Moment": "古き瞬間",
    "Glassfinger Toxin": "ガラス指の毒",
    "Ascendant Harmony": "上昇の調和",
    "Xanthotic Essence": "黄色のエッセンス",
    "Enduring Reflection": "永続する反射",
    "Rubywise Ruin": "ルビー色の破滅",
    "Frith-Weft": "平穏の横糸",
    "Cuckoo-Honey": "カッコウの蜂蜜",
    "Living Relic": "生きた遺物",
    "Chimeric Larva": "キメラの幼虫",
    "Asimel": "アシメル",
    "Perinculate": "ペリンクレイト",
    "Bitterblack Salts": "苦黒塩",
    "Iotic Essence": "紫のエッセンス",
    "Pale Mommet": "青ざめたモメット",
    "Winning Move": "勝利の二手",
    "Solomon’s Preparation": "ソロモンの調合",
    "Wire (Orichalcum)": "針金（オリハルコン）",
    "Wire (Silver)": "針金（銀）"
}

en_to_ja = {}
for item in data['items']:
    en_to_ja[item['name_en']] = item['name_ja']
en_to_ja.update(translations)

def translate_req(req):
    if req in categories:
        return categories[req]
    if req in en_to_ja:
        return en_to_ja[req]
    return req

with open('data/item_requirements.json', 'r', encoding='utf-8') as f:
    item_reqs = json.load(f)

for item in data['items']:
    en_name = item.get('name_en')
    if en_name in item_reqs:
        req = item_reqs[en_name]
        if req == "-":
            continue
            
        trans_req = translate_req(req)
        suffix = f" ＋【必須素材: {trans_req}】"
        
        # Append this suffix to any string in how_to_get that relates to crafting this level 10 or 15 item
        # Since this entire item requires it (it's the output of a 10/15 craft), any "クラフト" string in how_to_get should get it.
        if 'how_to_get' in item:
            new_htg = []
            for htg in item['how_to_get']:
                if "クラフト" in htg and "レベル5" not in htg and "5クラフト" not in htg:
                    if suffix not in htg:
                        new_htg.append(htg + suffix)
                    else:
                        new_htg.append(htg)
                else:
                    new_htg.append(htg)
            item['how_to_get'] = new_htg

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Inline appended requirements")
