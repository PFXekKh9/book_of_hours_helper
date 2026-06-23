import json
import bs4
import os
from pathlib import Path

CRAFTS_HTML_PATH = Path(os.environ.get("BOOK_OF_HOURS_CRAFTS_HTML", "wiki_sources/crafting.html"))

if not CRAFTS_HTML_PATH.exists():
    raise FileNotFoundError(
        f"Crafting wiki HTML not found: {CRAFTS_HTML_PATH}. "
        "Set BOOK_OF_HOURS_CRAFTS_HTML or place the file at wiki_sources/crafting.html."
    )

with CRAFTS_HTML_PATH.open('r', encoding='utf-8') as f:
    html_content = f.read()

soup = bs4.BeautifulSoup(html_content, 'html.parser')

skill_to_items = {}

for tr in soup.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) >= 2:
        item_a = tds[0].find('a')
        if not item_a:
            continue
        item_name = item_a.text.strip()
        
        for li in tds[1].find_all('li'):
            skill_name = li.text.strip()
            if skill_name not in skill_to_items:
                skill_to_items[skill_name] = []
            if item_name not in skill_to_items[skill_name]:
                skill_to_items[skill_name].append(item_name)

# There are also Prentice level crafts which are generic (e.g. Any Edge skill crafts X).
# But the wiki might not list every skill for generic crafts.
# We can just load the skills from somewhere and map them.
# The user wants "If I have Drums & Dances level 6, what can I craft?"

with open('frontend/public/data/skill_recipes.json', 'w', encoding='utf-8') as f:
    json.dump(skill_to_items, f, ensure_ascii=False, indent=2)

print("Saved skill_recipes.json to frontend/public/data/")
