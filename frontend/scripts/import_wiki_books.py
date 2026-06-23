import urllib.request
import json
import re
import os
import time
from bs4 import BeautifulSoup

def parse_mystery(text):
    match = re.search(r'([a-zA-Z]+)\s*(\d+)', text)
    if match:
        aspect = match.group(1).lower()
        val = int(match.group(2))
        if aspect in ['edge', 'forge', 'lantern', 'grail', 'heart', 'moth', 'knock', 'winter', 'moon', 'sky', 'scale', 'rose', 'nectar']:
            return aspect, val
    return None, None

def get_page(title):
    cache_path = f".cache_{title}.json"
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
            
    url = f"https://book-of-hours.fandom.com/api.php?action=parse&page={title}&format=json&prop=text"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Fetching {url}...")
    time.sleep(1)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            return data
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return None

def main():
    # Go up one dir since we are running inside frontend/scripts
    items_path = '../public/data/items.json'
    books_path = '../public/data/books.json'
    memory_sources_path = '../public/data/memory_sources.json'
    report_path = '../public/data/wiki_import_report.md'
    
    with open(items_path, 'r', encoding='utf-8') as f:
        items_data = json.load(f)
    
    memories = [i for i in items_data['items'] if i['category'] == 'memory']
    memory_dict_by_en = {m['name_en'].replace('Memory: ', ''): m for m in memories}
    memory_dict_by_id = {m['id']: m for m in memories}
    
    books = []
    unknown_memories = set()
    added_count = 0
    updated_count = 0
    needs_review_count = 0
    
    data = get_page('Readable')
    if not data: return
        
    soup = BeautifulSoup(data['parse']['text']['*'], 'html.parser')
    
    existing_books = []
    if os.path.exists(books_path):
        with open(books_path, 'r', encoding='utf-8') as f:
            existing_books = json.load(f)
            
    existing_book_dict = {b['id']: b for b in existing_books}
    
    for table in soup.find_all('table'):
        headers = [th.text.strip().lower() for th in table.find_all('th')]
        if 'name' not in headers or 'mystery' not in headers or 'memory' not in headers:
            continue
            
        name_idx = headers.index('name')
        mystery_idx = headers.index('mystery')
        lang_idx = headers.index('language') if 'language' in headers else -1
        memory_idx = headers.index('memory')
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) <= memory_idx: continue
            
            name_en = cols[name_idx].text.strip()
            if not name_en: continue
            
            mystery_text = cols[mystery_idx].text.strip()
            lang_text = cols[lang_idx].text.strip() if lang_idx >= 0 else ""
            if lang_text.lower() in ["", "none", "-", "n/a"]: lang_text = None
            
            memory_text = cols[memory_idx].text.strip().replace('Memory: ', '')
            
            diff_aspect, diff_val = parse_mystery(mystery_text)
            
            memory_id = None
            memory_name_ja = None
            memory_name_en = memory_text
            
            if memory_text in memory_dict_by_en:
                mem = memory_dict_by_en[memory_text]
                memory_id = mem['id']
                memory_name_ja = mem['name_ja']
            elif not memory_text or memory_text == "-":
                memory_name_en = None
            else:
                test_id = memory_text.lower().replace(' ', '_').replace('-', '_').replace("'", "")
                if test_id in memory_dict_by_id:
                    mem = memory_dict_by_id[test_id]
                    memory_id = mem['id']
                    memory_name_ja = mem['name_ja']
                    memory_name_en = mem['name_en']
                else:
                    unknown_memories.add(memory_text)
                    memory_id = test_id
                    memory_name_ja = "記憶：" + memory_text
            
            book_id = name_en.lower().replace(' ', '_').replace('-', '_').replace("'", "")
            
            # Duplication check by id
            original_id = book_id
            counter = 1
            while book_id in [b['id'] for b in books]:
                book_id = f"{original_id}_{counter}"
                counter += 1
            
            book = {
                "id": book_id,
                "name_ja": existing_book_dict.get(book_id, {}).get("name_ja", name_en),
                "name_en": name_en,
                "category": "book",
                "difficulty_aspect": diff_aspect,
                "difficulty_value": diff_val,
                "language": lang_text,
                "memory_on_reread": memory_id,
                "memory_name_ja": memory_name_ja,
                "memory_name_en": memory_name_en,
                "lessons": existing_book_dict.get(book_id, {}).get("lessons", []),
                "aspects": existing_book_dict.get(book_id, {}).get("aspects", {
                    "edge": 0, "forge": 0, "lantern": 0, "grail": 0, 
                    "heart": 0, "moth": 0, "knock": 0, "winter": 0, 
                    "moon": 0, "sky": 0, "scale": 0, "rose": 0, "nectar": 0
                }),
                "source_url": f"https://book-of-hours.fandom.com/wiki/{name_en.replace(' ', '_')}",
                "notes": existing_book_dict.get(book_id, {}).get("notes", "仮訳"),
                "needs_review": diff_aspect is None or memory_id is None,
                "owned_count": existing_book_dict.get(book_id, {}).get("owned_count", 0)
            }
            
            if book_id in existing_book_dict: updated_count += 1
            else: added_count += 1
                
            if book["needs_review"]: needs_review_count += 1
                
            books.append(book)

    with open(books_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
        
    memory_sources = {}
    for b in books:
        mem_id = b["memory_on_reread"]
        if not mem_id: continue
        
        if mem_id not in memory_sources:
            mem = memory_dict_by_id.get(mem_id, {})
            memory_sources[mem_id] = {
                "memory_id": mem_id,
                "memory_name_ja": b["memory_name_ja"],
                "memory_name_en": b["memory_name_en"],
                "aspects": mem.get("aspects", {}),
                "books": []
            }
        
        memory_sources[mem_id]["books"].append({
            "book_id": b["id"],
            "name_ja": b["name_ja"],
            "name_en": b["name_en"],
            "difficulty_aspect": b["difficulty_aspect"],
            "difficulty_value": b["difficulty_value"],
            "language": b["language"],
            "source_url": b["source_url"]
        })
        
    with open(memory_sources_path, 'w', encoding='utf-8') as f:
        json.dump(list(memory_sources.values()), f, ensure_ascii=False, indent=2)
        
    report = f"""# Wiki Import Report (Books & Memory Sources)

* Total Books Processed: {len(books)}
* Added: {added_count}
* Updated: {updated_count}
* Needs Review: {needs_review_count}

## Unknown Memories
The following memories were referenced by books but not found in `items.json`:
"""
    for m in unknown_memories: report += f"* {m}\n"
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Done. Processed {len(books)} books.")

if __name__ == "__main__":
    main()
