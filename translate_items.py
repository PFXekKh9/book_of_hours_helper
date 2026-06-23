import json

with open('data/items.json', 'r') as f:
    data = json.load(f)

translations = {
    "Consider any Wall Art": "壁の絵などを検討",
    "Consider most Comforts": "ほとんどの快適な家具などを検討",
    "Consider Hush House Key, throw something in the Hush House Well": "沈黙の家の鍵を検討、沈黙の家の井戸に物を投げる",
    "Discard anything at Sea's Edge": "海辺で何かを捨てる",
    "Swim at Sea's Edge": "海辺で泳ぐ",
    "Swim with Basket of Towels at Sea's Edge": "海辺で泳ぎ、タオルのかごで乾かす",
    "Discard a Penny at Sea's Edge": "海辺でペニーを捨てる",
    "Discard a Penny at the Well": "井戸にペニーを投げる",
    "Consume Bitterblack Salts or Watchful Candle": "ビターブラックの塩か見守るロウソクを消費する",
    "Scholar 00Edge": "刃の学者",
    "Keeper 00Rose, Considering Gervinite, Talking to Stymphling, Gathering from the Gull Colony in Numa": "薔薇の番人、ゲルビナイトを検討、スティンフリングと会話、ヌマの時期にカモメのコロニーから採集",
    "Talk to StymphlingDiscard a penny at Sea's Edge in Numa": "スティンフリングと会話、ヌマの時期に海辺でペニーを捨てる",
    "Keeper 00Sky": "空の番人",
    "Reading, Talking to Viper": "読書、毒蛇と会話",
    "Talk to Viper": "毒蛇と会話",
    "Read De Ratio Quercuum or Rapt in the King": "「De Ratio Quercuum」か「Rapt in the King」を読む",
    "Consider Yellowing Newspaper": "黄ばんだ新聞を検討",
    "Considering Yellowing Newspaper": "黄ばんだ新聞を検討",
    "Keeper 00Edge": "刃の番人",
    "Scholar 00Heart": "心の学者",
    "Consider Nighted Chair, gather from sea caves": "夜の椅子を検討、海の洞窟から採集",
    "Talk with Green Cockatoo": "ミドリインコと会話",
    "Consume Ichor Auroral": "暁の霊液を消費",
    "Consume Refulgin": "レフルギンを消費",
    "Consume a Historywax Candle": "歴史蝋のロウソクを消費",
    "Consider a Historywax Candle": "歴史蝋のロウソクを検討",
    "Talk to a Pet Gull": "ペットのカモメと会話",
    "Talking to a Gull, Gathering during Numa": "カモメと会話、ヌマの時期に採集",
    "Scholar 00Rose, Gathering in Numa": "薔薇の学者、ヌマの時期に採集",
    "Scholar 00Sky": "空の学者",
    "Talk to Perilous ImagoGather from the Beehive": "危険な成虫と会話、ミツバチの巣から採集",
    "Scholar 00Nectar, Talking to Perilous Imago, Gathering from the Beehive": "蜜の学者、危険な成虫と会話、ミツバチの巣から採集",
    "Scholar 00Knock, Swimming in Numa": "開門の学者、ヌマの時期に泳ぐ",
    "Keeper 00Moon": "月の番人",
    "Towards a Fundamental Aesthetic": "根本的な美学に向けて",
    "The Sky in the Scar": "傷跡の空",
    "Kopralith Omphalos": "コプラリスのへそ",
    "The Sun Disfigured": "傷つけられた太陽",
    "Amiranis Beteli": "アミラニのベテリ",
    "A Child's Treasury of Golden Afternoons": "子供の黄金の午後の宝物庫",
    "Shuritic Book of Suns": "シュライトの太陽の書",
    "The Turquoise Hand": "ターコイズの手",
    "The Sun's Design": "太陽の設計",
    "The Writing on the Wall": "壁の落書き",
}

name_translations = {
    "Misshapen Fruit": "奇形果実",
    "Moly": "モーリー",
    "Canned Ham": "缶詰のハム",
    "Hen's Egg": "鶏の卵",
    "Viper Egg": "毒蛇の卵",
    "Gull's Egg": "カモメの卵",
    "Almonds": "アーモンド",
    "Beef": "牛肉",
    "Blackberries": "ブラックベリー",
    "Bottle of Milk": "牛乳瓶",
    "Mushrooms": "キノコ",
    "Pheasant": "キジ",
    "Pilchards": "イワシ",
    "Rosehips": "ローズヒップ",
    "Kitchen Bowls": "キッチンボウル",
    "Mortar & Pestle": "乳鉢と乳棒",
    "Dearday Lens": "ディアデイ・レンズ",
    "Flushed Mommet": "上気したマメット",
    "Pale Mommet": "蒼白なマメット",
    "Swaddled Thunder": "包まれた雷"
}

for item in data['items']:
    if item['name_en'] in name_translations and item['name_ja'] == item['name_en']:
        item['name_ja'] = name_translations[item['name_en']]
    
    new_htg = []
    for htg in item.get('how_to_get', []):
        if htg in translations:
            new_htg.append(translations[htg])
        else:
            new_htg.append(htg)
    
    # Remove duplicates but preserve order
    seen = set()
    dedup = []
    for x in new_htg:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
            
    if 'how_to_get' in item:
        item['how_to_get'] = dedup

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done translating items.json")
