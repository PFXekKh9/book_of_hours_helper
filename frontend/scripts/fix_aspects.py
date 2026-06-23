import json

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    fixed_count = 0
    for item in data['items']:
        for asp, val in item.get('aspects', {}).items():
            if val > 10:
                item['aspects'][asp] = val // 100
                fixed_count += 1
                
    if fixed_count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Fixed {fixed_count} aspects in {path}")

fix_file('public/data/items.json')
