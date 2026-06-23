import json

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
    "Winning Move": "勝利の二手"
}

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data['items']:
    if 'how_to_get' in item:
        new_htg = []
        for htg in item['how_to_get']:
            if "必須素材:" in htg:
                for en, ja in translations.items():
                    htg = htg.replace(en, ja)
            new_htg.append(htg)
        item['how_to_get'] = new_htg

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Translated required items in items.json")
