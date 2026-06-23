import json

translations = {
    "Anbary & Lapidary": "琥珀金と宝石細工",
    "Applebright Euphonies": "リンゴの輝き",
    "Auroral Contemplations": "極光の黙想",
    "Bells & Brazieries": "鐘と火鉢",
    "Coil & Chasm": "とぐろと裂け目",
    "Desires & Dissolutions": "欲望と溶解",
    "Disciplines of the Hammer": "槌の修練",
    "Disciplines of the Scar": "傷の修練",
    "Door & Wall": "扉と壁",
    "Drums & Dances": "ドラム、そして舞踊",
    "Edicts Inviolable": "不可侵の布告",
    "Edicts Liminal": "境界の布告",
    "Edicts Martial": "軍事の布告",
    "Furs & Feathers": "毛皮と羽",
    "Glassblowing & Vesselcrafting": "吹きガラスと器作り",
    "Glaziery & Lightsmithing": "ガラス細工と光の鍛造",
    "Herbs & Infusions": "ハーブと煎じ薬",
    "Hill & Hollow": "丘と窪み",
    "Horns & Ivories": "角と象牙",
    "Inks of Containment": "封じ込めのインク",
    "Inks of Power": "力のインク",
    "Inks of Revelation": "啓示のインク",
    "Insects & Nectars": "昆虫学と蜜",
    "Leaves & Thorns": "葉と棘",
    "Lockworks & Clockworks": "錠前と時計仕掛け",
    "Maggephene Mysteries": "マゲフェネの神秘",
    "Meniscate Reflections": "メニスカテの反射",
    "Orchids & Narcotics": "蘭と麻薬",
    "Ouranoscopy": "天体観測",
    "Path & Pilgrim": "道と巡礼者",
    "Pearl & Tide": "真珠と潮",
    "Pentiments & Precursors": "ペンティメントと先駆者",
    "Preliminal Meter": "境界の韻律",
    "Purifications & Exaltations": "浄化と高揚",
    "Putrefactions & Calcinations": "腐敗と灰化",
    "Pyroglyphics": "炎の象形文字",
    "Quenchings & Quellings": "焼入れと鎮圧",
    "Ragged Crossroads": "ぼろぼろの交差点",
    "Resurgences & Emergences": "復活と出現",
    "Rhyme & Remembrance": "韻と記憶",
    "Rhyme & Reason": "韻と理",
    "Rites of the Roots": "根の儀式",
    "Sacra Limiae": "限界の聖務",
    "Sacra Solis Invicti": "不屈の太陽の聖務",
    "Sand Stories": "砂の物語",
    "Sea Stories": "海の物語",
    "Serpents & Venoms": "蛇と毒",
    "Sharps": "鋭利",
    "Sickle & Eclipse": "鎌と日食",
    "Sights & Sensations": "視覚と感覚",
    "Sky Stories": "空の物語",
    "Snow Stories": "雪の物語",
    "Solutions & Separations": "溶解と分離",
    "Spices & Savours": "香辛料と風味",
    "Stitching & Binding": "縫合と製本",
    "Stone Stories": "石の物語",
    "Strings & Songs": "弦と歌",
    "Surgeries & Exsanguinations": "外科手術と瀉血",
    "The Great Signs and the Great Scars": "大いなる兆候と大いなる傷",
    "Transformations & Liberations": "変容と解放",
    "Tridesma Hiera": "トリデスマ・ヒエラ",
    "Watchman's Paradoxes": "見張りの逆説",
    "Weaving & Knotworking": "織物と結び目細工",
    "Wolf Stories": "狼の物語",
    "Cracktrack": "クラックトラック",
    "Deep Mandaic": "深淵マンダ語",
    "Ericapaean": "エリカパイオス語",
    "Fucine": "フュシン語",
    "Henavek": "ヘナヴェク語",
    "Hyksos": "ヒクソス語",
    "Killasimi": "キラシミ語",
    "Ramsund": "ラムスンド語",
    "Sabazine": "サバジン語",
    "Vak": "ヴァク語",
    "Apple-bright": "リンゴの輝き"
}

with open('data/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sort translation keys by length descending to prevent partial replacements
sorted_keys = sorted(translations.keys(), key=len, reverse=True)

for item in data['items']:
    if 'how_to_get' in item and item['how_to_get']:
        new_htg = []
        for htg in item['how_to_get']:
            # For each string, replace any occurrence of the English skill name with the Japanese one.
            new_str = htg
            for en in sorted_keys:
                if en in new_str:
                    new_str = new_str.replace(en, translations[en])
            new_htg.append(new_str)
        item['how_to_get'] = new_htg

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated how_to_get in items.json with Japanese skill names.")
