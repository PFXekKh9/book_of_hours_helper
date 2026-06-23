import json
import bs4
import os
from pathlib import Path

SKILLS_HTML_PATH = Path(os.environ.get("BOOK_OF_HOURS_SKILLS_HTML", "wiki_sources/skills.html"))

if not SKILLS_HTML_PATH.exists():
    raise FileNotFoundError(
        f"Skills wiki HTML not found: {SKILLS_HTML_PATH}. "
        "Set BOOK_OF_HOURS_SKILLS_HTML or place the file at wiki_sources/skills.html."
    )

with SKILLS_HTML_PATH.open('r', encoding='utf-8') as f:
    html_content = f.read()

soup = bs4.BeautifulSoup(html_content, 'html.parser')

skills = []

for tr in soup.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) >= 4:
        skill_a = tds[0].find('a')
        if not skill_a:
            continue
        skill_name = skill_a.text.strip()
        if not skill_name:
            continue
            
        # Aspects are usually in tds[1] and tds[2] or inside spans
        # The Skills table format: Name, Aspect 1, Aspect 2, Wisdom
        aspects = []
        for i in range(1, 3):
            asp_tag = tds[i].find('a')
            if asp_tag and asp_tag.get('title'):
                asp_title = asp_tag.get('title').lower().strip()
                # filter out non-aspect things if any, but they should be aspects
                if asp_title in ['edge', 'forge', 'lantern', 'grail', 'heart', 'moth', 'knock', 'winter', 'moon', 'sky', 'scale', 'rose', 'nectar']:
                    aspects.append(asp_title)
                    
        if len(aspects) > 0:
            skills.append({
                "id": skill_name.lower().replace(" ", "_").replace("&", "and"),
                "name_en": skill_name,
                "name_ja": skill_name, # Fallback, we can map this later if needed
                "aspects": aspects
            })

with open('frontend/public/data/skills.json', 'w', encoding='utf-8') as f:
    json.dump({"skills": skills}, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(skills)} skills.")
