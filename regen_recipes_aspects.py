import json
import bs4
import re
import os
from pathlib import Path

# 1. Load the skills translation map
with open('frontend/public/data/skills.json', 'r', encoding='utf-8') as f:
    skills_data = json.load(f)

skill_translations = {}
for s in skills_data.get('skills', []):
    skill_translations[s['name_en']] = s['name_ja']

# 2. Load the item translation map from items.json (to translate outputs and requirements)
with open('data/items.json', 'r', encoding='utf-8') as f:
    items_data = json.load(f)

item_translations = {
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
    "Wire (Silver)": "針金（銀）",
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
}

aspect_translations = {
    "edge": "刃",
    "forge": "鍛造",
    "grail": "聖杯",
    "heart": "心",
    "knock": "啓開",
    "lantern": "灯",
    "moon": "月",
    "moth": "蛾",
    "nectar": "蜜",
    "rose": "薔薇",
    "scale": "鱗",
    "sky": "空",
    "winter": "冬"
}

for item in items_data['items']:
    item_translations[item['name_en']] = item.get('name_ja', item['name_en'])

CRAFTS_HTML_PATH = Path(os.environ.get("BOOK_OF_HOURS_CRAFTS_HTML", "wiki_sources/crafting.html"))

if not CRAFTS_HTML_PATH.exists():
    raise FileNotFoundError(
        f"Crafting wiki HTML not found: {CRAFTS_HTML_PATH}. "
        "Set BOOK_OF_HOURS_CRAFTS_HTML or place the file at wiki_sources/crafting.html."
    )

# 3. Parse crafting wiki HTML
with CRAFTS_HTML_PATH.open('r', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f.read(), 'html.parser')

item_recipes = {} # en_name -> list of string descriptions

for table in soup.find_all('table', class_='fandom-table'):
    table_id = table.get('id', '')
    
    # Extract aspect and level from table id
    # e.g., mw-customcollapsible-edge-prentice
    aspect_en = "unknown"
    level_en = "unknown"
    match = re.search(r'mw-customcollapsible-([a-z]+)-([a-z]+)', table_id)
    if match:
        aspect_en = match.group(1)
        level_en = match.group(2)
        
    aspect_ja = aspect_translations.get(aspect_en, aspect_en.capitalize())
    
    level_name = "不明"
    level_val = "0"
    if level_en == "prentice":
        level_name = f"徒弟の{aspect_ja}"
        level_val = "5"
    elif level_en == "scholar":
        level_name = f"学者の{aspect_ja}"
        level_val = "10"
    elif level_en == "keeper":
        level_name = f"番人の{aspect_ja}"
        level_val = "15"
            
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 6:
            item_a = tds[0].find('a')
            if not item_a: continue
            crafted_en = item_a.text.strip()
            
            skills_en = [li.text.strip() for li in tds[1].find_all('li')]
            skills_ja = [skill_translations.get(s, s) for s in skills_en]
            
            reqs = []
            req_a = tds[5].find('a')
            if req_a:
                reqs.append(req_a.text.strip())
            else:
                rt = tds[5].text.strip()
                if rt and rt != "-":
                    reqs.append(rt)
                    
            req_ja = [item_translations.get(r, r) for r in reqs]
            
            skills_str = ", ".join(skills_ja)
            
            recipe_str = f"クラフト: {level_name}(レベル{level_val}) （必要なスキル: {skills_str}）"
            if req_ja and req_ja[0] != "-" and req_ja[0]:
                recipe_str += f" ＋【必須素材: {req_ja[0]}】"
                
            if crafted_en not in item_recipes:
                item_recipes[crafted_en] = []
            if recipe_str not in item_recipes[crafted_en]:
                item_recipes[crafted_en].append(recipe_str)

# 4. Update items.json
for item in items_data['items']:
    en_name = item.get('name_en')
    
    cleaned_htg = []
    for htg in item.get('how_to_get', []):
        if "クラフト" not in htg and "必須素材" not in htg and "5クラフト" not in htg and "10クラフト" not in htg and "15クラフト" not in htg:
            cleaned_htg.append(htg)
            
    if en_name in item_recipes:
        cleaned_htg = item_recipes[en_name] + cleaned_htg
        
    item['how_to_get'] = cleaned_htg

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(items_data, f, ensure_ascii=False, indent=2)

print("Regenerated precise crafting recipes with attributes for all items!")
