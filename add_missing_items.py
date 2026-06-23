import json

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('data/skill_recipes.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# Collect all items from items.json
existing_names = set(i['name_en'] for i in data['items'] if 'name_en' in i)

translations = {
    "Mazarine Fife": "マザリン・ファイフ",
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
    "Wire (Silver)": "針金（銀）",
    "Sacrament Malachite": "サクラメント・マラカイト",
    "Sacrament Ascite": "サクラメント・アスカイト",
    "Sacrament Calicite": "サクラメント・キャリサイト",
    "Ashartine": "アシャルティーン",
    "Uzult": "ウズルト",
    "Marakat": "マラカット",
    "Catwink": "キャットウィンク",
    "Witching Tisane": "魔女のハーブティー",
    "Thirza's Cordials": "ティルザのコーディアル",
    "Gideon's Soaks": "ギデオンの酒",
    "Black Sapphire Wash": "ブラックサファイア・ウォッシュ",
    "Yewgall Ink": "イチイコブのインク",
    "Stargall Ink": "星虫瘤のインク",
    "Awakened Feather": "目覚めた羽",
    "Eigengrau": "アイゲングラウ",
    "Houndsgall": "猟犬の胆汁",
    "Nillycant": "ニリキャント",
    "Orpiment Exultant": "雄黄の歓喜",
    "Paint: Moth-Gold": "絵の具：蛾の金",
    "Regensburg Balm": "レーゲンスブルクの軟膏",
    "Salt-Sign": "塩の徴",
    "Tanglebrag": "タングルブラグ",
    "Wyrd-Weft": "運命の横糸",
    "Year-Tally": "年の記録",
    "Year Tally": "年の記録",
    "Bisclavret's Knot": "ビスクラヴレの結び目",
    "Gervinite": "ジェルヴィナイト",
    "January Sanguinary": "一月の血",
    "Perilous Imago": "危険なイマゴ",
    "Porphyrine": "ポルフィリン",
    "Westcott's Compounds": "ウェスコットの混合物",
    "Amethyst Ampoule": "アメジストのアンプル",
    "Azoth": "アゾット",
    "Labhitic Tincture": "ラビシック・チンキ",
    "Midnight Mark": "真夜中の印",
    "Perhibiate": "パーヒビエイト",
    "Refulgin": "リフルギン",
    "Serpent-Milk": "蛇の乳"
}

added_count = 0
for skill, item_list in recipes.items():
    for recipe_item in item_list:
        en_name = recipe_item['item_name_en']
        if en_name not in existing_names:
            # We need to add this item to items.json!
            ja_name = translations.get(en_name, en_name)
            
            # Infer category somewhat from the name
            cat = "crafted"
            if "Sacrament" in en_name or "Tisane" in en_name or "Soaks" in en_name or "Cordials" in en_name or "Leathy" in en_name:
                cat = "drink"
            elif "Ink" in en_name or "Wash" in en_name:
                cat = "tool" # or ink
                
            new_item = {
                "id": en_name.lower().replace(" ", "_").replace("'", "").replace("-", "_"),
                "name_ja": ja_name,
                "name_en": en_name,
                "category": cat,
                "aspects": {}, # We might not know its aspects right now
                "how_to_get": [],
                "locations": [],
                "recipe": None,
                "rarity": "common",
                "tags": []
            }
            
            # Add basic craft info so it shows up
            # Actually, the craft info is populated by `skill_recipes.json` but in CraftingMode, it checks `item.craft.level`
            # Wait, `CraftingMode.tsx` checks `if ((item.craft.level === 10 || item.craft.level === 15) ...)`
            # We don't have the exact level here unless we guess from the recipe.
            # `skill_recipes.json` has "levels: [10]" or "levels: [15]"!
            levels = recipe_item.get('levels', [])
            level = min(levels) if levels else 5
            
            # Principle can be one of the aspects from the recipe_item
            aspects = recipe_item.get('aspects', [])
            principle = aspects[0] if aspects else "unknown"
            
            new_item["craft"] = {
                "principle": principle,
                "level": level
            }
            
            data['items'].append(new_item)
            existing_names.add(en_name)
            added_count += 1

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added_count} missing crafted items to items.json")
