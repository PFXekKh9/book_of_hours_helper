import React, { useEffect, useState } from 'react';
import type { Item, MemorySource } from '../data';
import { fetchItems, fetchMemorySources, ASPECT_ICONS, ASPECT_NAMES_JA, CATEGORY_LABELS, formatItemName } from '../data';
const DictionaryMode: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [memorySources, setMemorySources] = useState<MemorySource[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAspects, setSelectedAspects] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchItems().then(setItems);
    fetchMemorySources().then(setMemorySources);
  }, []);

  const toggleAspect = (asp: string) => {
    if (selectedAspects.includes(asp)) {
      setSelectedAspects(selectedAspects.filter(a => a !== asp));
    } else {
      setSelectedAspects([...selectedAspects, asp]);
    }
  };

  const filteredItems = items.filter(item => {
    const matchSearch = item.name_ja.toLowerCase().includes(searchTerm.toLowerCase()) || 
                        item.name_en.toLowerCase().includes(searchTerm.toLowerCase());
    const matchAspect = selectedAspects.length === 0 || 
                        selectedAspects.some(asp => item.aspects && item.aspects[asp] !== undefined);
    const matchCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchSearch && matchAspect && matchCategory;
  });

  return (
    <div>
      <h2 className="mb-4 text-gradient">アイテム辞典</h2>
      <div className="flex gap-4 mb-4 flex-wrap">
        <input 
          type="text" 
          className="input-field" 
          style={{ flex: '1', minWidth: '200px' }}
          placeholder="アイテム名で検索..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select 
          className="input-field"
          style={{ width: 'auto' }}
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="all">すべてのカテゴリ</option>
          {Object.entries(CATEGORY_LABELS).map(([cat, label]) => (
            <option key={cat} value={cat}>{label}</option>
          ))}
        </select>
      </div>

      <div className="flex gap-2 mb-6 flex-wrap">
        {Object.entries(ASPECT_ICONS).map(([asp, icon]) => (
          <button 
            key={asp} 
            className={`filter-chip ${selectedAspects.includes(asp) ? 'active' : ''}`}
            onClick={() => toggleAspect(asp)}
          >
            {icon} {ASPECT_NAMES_JA[asp] || asp}
          </button>
        ))}
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
        {filteredItems.map(item => (
          <div key={item.id} className="glass-panel p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 style={{ fontSize: '1.1em' }}>{formatItemName(item)}</h3>
              <span className="aspect-badge">{CATEGORY_LABELS[item.category] || item.category}</span>
            </div>
            
            <div className="flex gap-2 flex-wrap mb-2">
              {Object.entries(item.aspects).map(([asp, val]) => (
                <span key={asp} className="aspect-badge">
                  {ASPECT_ICONS[asp]} {asp} +{val}
                </span>
              ))}
            </div>

            <div style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>
              {item.persistent && <div style={{ color: 'var(--primary-hover)' }}>✓ 持続記憶</div>}
              {((item.how_to_get && item.how_to_get.length > 0) || (memorySources.find(m => m.memory_id === item.id)?.books?.length || 0) > 0) && (
                <div className="mt-2">
                  <strong>入手方法:</strong>
                  <ul style={{ paddingLeft: '20px', marginTop: '4px' }}>
                    {(item.how_to_get || []).map((htg, i) => {
                      if (htg === "対応本を再読" || htg.startsWith("特定の")) {
                        // Skip rendering these manually since we handle books globally below
                        return null;
                      }
                      return <li key={i}>{htg}</li>;
                    })}
                    {/* Add corresponding books automatically if they exist */}
                    {(() => {
                      const ms = memorySources.find(m => m.memory_id === item.id);
                      if (ms && ms.books && ms.books.length > 0) {
                        return (
                          <li key="books">
                            以下の本を再読:
                            <ul style={{ paddingLeft: '16px', marginTop: '2px', fontSize: '0.9em', color: 'var(--text-main)' }}>
                              {ms.books.map(b => (
                                <li key={b.book_id}>
                                  <a href={b.source_url} target="_blank" rel="noreferrer" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
                                    {b.name_ja && b.name_ja !== b.name_en ? b.name_ja : b.name_en}
                                  </a>
                                </li>
                              ))}
                            </ul>
                          </li>
                        );
                      }
                      return null;
                    })()}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DictionaryMode;
