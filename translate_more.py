import json
import re

with open('data/items.json', 'r') as f:
    data = json.load(f)

translation_dict = {
    "Consider Paradise Palm in Grand Ascent - Ground Floor": "大階段一階の極楽ヤシを検討",
    "Consume most food/drink": "ほとんどの飲食物を消費",
    "Re-read certain 00Knock Books": "特定の開門の本を再読",
    "Re-read certain 00Edge Books": "特定の刃の本を再読",
    "Crafting: Prentice 00Grail": "クラフト：徒弟の聖杯",
    "Crafting: Prentice 00Winter/00Moon": "クラフト：徒弟の冬/月",
    "Crafting: Prentice 00Heart": "クラフト：徒弟の心",
    "Crafting: Prentice 00Nectar/00Scale": "クラフト：徒弟の蜜/鱗",
    "Crafting: Prentice 00Sky": "クラフト：徒弟の空",
    "Crafting: Prentice 00Edge/00Sky": "クラフト：徒弟の刃/空",
    "Crafting: Prentice 00Knock": "クラフト：徒弟の開門",
    "Crafting: Prentice 00Moon/00Rose/00Sky": "クラフト：徒弟の月/薔薇/空",
    "Crafting: Scholar 00Moth": "クラフト：学者の蛾",
    "Crafting: Scholar 00Edge": "クラフト：学者の刃",
    "Crafting: Scholar 00Lantern/00Scale, consume cuckoo-honey, talk to living relic": "クラフト：学者の灯/鱗、カッコウの蜂蜜を消費、生きた遺物と会話",
    "Scholar 00Lantern/00Scale": "学者の灯/鱗",
    "Crafting: Keeper 00Rose": "クラフト：番人の薔薇",
    "Crafting: Keeper 00Sky": "クラフト：番人の空",
    "Talk to Viper": "毒蛇と会話",
    "Read De Ratio Quercuum or Rapt in the King": "「De Ratio Quercuum」か「Rapt in the King」を読む",
    "Crafting: Keeper 00Edge": "クラフト：番人の刃",
    "Keeper 00Lantern/00Scale": "番人の灯/鱗",
    "Crafting: Keeper 00Lantern/00Scale": "クラフト：番人の灯/鱗",
    "Crafting: Scholar 00Heart": "クラフト：学者の心",
    "Consume Moth-Orchid-Scented Candle": "蛾蘭の香りのロウソクを消費",
    "Talk with The Blacksmith (21%) or The Rector (17%)": "鍛冶屋（21%）か教区長（17%）と会話",
    "Consume unpleasant food, talk with The Midwife (17%), harvest from beehive in fall": "不快な食べ物を消費、助産師（17%）と会話、秋にミツバチの巣から収穫",
    "Talk with Seasonal/Unusual assistants (6%)": "季節限定/珍しい支援者と会話（6%）",
    "Crafting: Prentice 00Moon": "クラフト：徒弟の月",
    "Gather at The Sea-Caves during Numa (25%)": "ヌマの時期に海の洞窟で採集（25%）",
    "Crafting: Scholar 00Rose": "クラフト：学者の薔薇",
    "Crafting: Scholar 00Sky": "クラフト：学者の空",
    "Crafting: Scholar 00Nectar": "クラフト：学者の蜜",
    "Crafting: Scholar 00Knock": "クラフト：学者の開門",
    "Crafting: Scholar/Keeper 00Moon": "クラフト：学者/番人の月",
    "Scholar/Keeper 00Moon": "学者/番人の月",
    "Crafting: Keeper 00Moon": "クラフト：番人の月",
    "Towards a Fundamental Aesthetic: Second Edition": "根本的な美学に向けて：第二版",
    "Serpent-Root": "蛇の根",
    "The Three and the Three (St Chiavi Manuscript)": "三と三（聖キアヴィ写本）"
}

def translate_htg(htg_list):
    new_htg = []
    for htg in htg_list:
        translated = htg
        for en, ja in translation_dict.items():
            if en in translated:
                translated = translated.replace(en, ja)
        new_htg.append(translated)
    
    # Remove duplicates but preserve order
    seen = set()
    dedup = []
    for x in new_htg:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return dedup

for item in data['items']:
    if 'how_to_get' in item:
        item['how_to_get'] = translate_htg(item['how_to_get'])

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done translating more items.json")
