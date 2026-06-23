import json
import bs4
import os
from pathlib import Path

# Dictionary to translate some common skills to Japanese if known
# (We can just use a simple translation or leave them in English)
skill_translation = {
    "Weaving & Knotworking": "織物と結び目細工",
    "Edicts Liminal": "境界の布告",
    "Rites of the Roots": "根の儀式",
    "Sacra Limiae": "限界の聖務",
    "Solutions & Separations": "溶解と分離",
    "Insects & Nectars": "昆虫学と蜜",
    "Rhyme & Reason": "韻と理",
    "Sharpening & Finishing": "研磨と仕上げ",
    "Hill & Hollow": "丘と窪み",
    "Sand & Sea": "砂と海",
    "Apple-bright": "リンゴの輝き",
    # We can just leave unknown ones in English
}

CRAFTS_HTML_PATH = Path(os.environ.get("BOOK_OF_HOURS_CRAFTS_HTML", "wiki_sources/crafting.html"))

if not CRAFTS_HTML_PATH.exists():
    raise FileNotFoundError(
        f"Crafting wiki HTML not found: {CRAFTS_HTML_PATH}. "
        "Set BOOK_OF_HOURS_CRAFTS_HTML or place the file at wiki_sources/crafting.html."
    )

# 1. Parse the wiki HTML
with CRAFTS_HTML_PATH.open('r', encoding='utf-8') as f:
    html_content = f.read()

soup = bs4.BeautifulSoup(html_content, 'html.parser')

item_to_skills = {}

for tr in soup.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) >= 2:
        item_a = tds[0].find('a')
        if not item_a:
            continue
        item_name = item_a.text.strip()
        
        # Determine the level if available (column 4 or 3?)
        # Let's just grab all skills regardless of level, we'll only update 10/15 crafts later.
        skills = []
        for li in tds[1].find_all('li'):
            skill_name = li.text.strip()
            skills.append(skill_name)
            
        if skills:
            if item_name not in item_to_skills:
                item_to_skills[item_name] = []
            item_to_skills[item_name].extend(skills)

# 2. Update items.json
with open('data/items.json', 'r') as f:
    data = json.load(f)

for item in data['items']:
    craft_info = item.get('craft')
    if craft_info and craft_info.get('level') in (10, 15):
        en_name = item.get('name_en')
        if en_name in item_to_skills:
            skills = item_to_skills[en_name]
            # remove duplicates
            skills = list(dict.fromkeys(skills))
            
            # Translate skills
            ja_skills = [skill_translation.get(s, s) for s in skills]
            
            # Format the required skills string
            skill_str = "必要なスキル: " + ", ".join(ja_skills)
            
            # Find the existing craft string in how_to_get and replace it, or add to it
            new_htg = []
            replaced = False
            for htg in item.get('how_to_get', []):
                if "クラフト" in htg and str(craft_info['level']) not in htg:
                    # E.g. "クラフト：学者の蛾"
                    new_htg.append(f"{htg} （{skill_str}）")
                    replaced = True
                elif "クラフト" in htg:
                    # E.g. "蛾10クラフト"
                    new_htg.append(f"{htg} （{skill_str}）")
                    replaced = True
                else:
                    new_htg.append(htg)
            
            if not replaced:
                new_htg.append(f"クラフト レベル{craft_info['level']} （{skill_str}）")
            
            item['how_to_get'] = new_htg

with open('data/items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Skill requirements added to items.json")
