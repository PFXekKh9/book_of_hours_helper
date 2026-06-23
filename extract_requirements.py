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

item_requirements = {}

for tr in soup.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) >= 6:
        item_a = tds[0].find('a')
        if not item_a:
            continue
        item_name = item_a.text.strip()
        
        # tds[5] is the "Additional Requirements"
        req_a = tds[5].find('a')
        if req_a:
            req_name = req_a.text.strip()
            # sometimes there might be text without a link, but usually it's linked
            if req_name:
                item_requirements[item_name] = req_name
        else:
            req_text = tds[5].text.strip()
            if req_text:
                item_requirements[item_name] = req_text

with open('data/item_requirements.json', 'w', encoding='utf-8') as f:
    json.dump(item_requirements, f, ensure_ascii=False, indent=2)

print(f"Extracted requirements for {len(item_requirements)} items.")
