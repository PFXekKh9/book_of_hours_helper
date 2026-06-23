import React, { useEffect, useState, useMemo } from 'react';
import type { AspectMap, Book, MemorySource } from '../data';
import { fetchBooks, fetchMemorySources, ASPECT_ICONS, ASPECT_NAMES_JA, formatItemName } from '../data';
const BooksMode: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [memorySources, setMemorySources] = useState<MemorySource[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [memoryFilter, setMemoryFilter] = useState('');
  const [aspectFilter, setAspectFilter] = useState('');
  const [aspectMinVal, setAspectMinVal] = useState(1);
  const [onlyOwned, setOnlyOwned] = useState(false);
  const [inventory, setInventory] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchBooks().then(data => {
      setBooks(data);
      const inv: Record<string, number> = {};
      data.forEach(b => {
        if (b.owned_count > 0) inv[b.id] = b.owned_count;
      });
      setInventory(inv);
    });
    fetchMemorySources().then(setMemorySources);
  }, []);

  const handleInventoryChange = (id: string, val: number) => {
    setInventory(prev => ({ ...prev, [id]: Math.max(0, val) }));
  };

  // Find memory by ID to show its aspects
  const getMemoryAspects = (memoryId: string | null): AspectMap | null => {
    if (!memoryId) return null;
    const src = memorySources.find(m => m.memory_id === memoryId);
    return src ? src.aspects : null;
  };

  const filteredBooks = useMemo(() => {
    return books.filter(b => {
      if (onlyOwned && (inventory[b.id] || 0) === 0) return false;

      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const matchName = b.name_ja.toLowerCase().includes(searchLower) || b.name_en.toLowerCase().includes(searchLower);
        if (!matchName) return false;
      }

      if (memoryFilter) {
        const memLower = memoryFilter.toLowerCase();
        const memJa = b.memory_name_ja?.toLowerCase() || '';
        const memEn = b.memory_name_en?.toLowerCase() || '';
        if (!memJa.includes(memLower) && !memEn.includes(memLower)) return false;
      }

      if (aspectFilter) {
        const memoryAspects = getMemoryAspects(b.memory_on_reread);
        if (!memoryAspects || (memoryAspects[aspectFilter] || 0) < aspectMinVal) {
           return false;
        }
      }

      return true;
    });
  }, [books, inventory, searchTerm, memoryFilter, aspectFilter, aspectMinVal, onlyOwned, memorySources]);

  return (
    <div>
      <h2 className="mb-4 text-gradient">本 / Books</h2>
      
      <div className="glass-panel p-4 mb-6">
        <h3 className="mb-4">検索・フィルター</h3>
        <div className="flex gap-4 flex-wrap">
          <div className="flex-col gap-2" style={{ flex: '1 1 200px' }}>
            <label>本名で検索</label>
            <input 
              type="text" 
              className="input-field" 
              placeholder="アポロとマルシュアス..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex-col gap-2" style={{ flex: '1 1 200px' }}>
            <label>再読記憶名で逆引き</label>
            <input 
              type="text" 
              className="input-field" 
              placeholder="嵐, Storm..." 
              value={memoryFilter}
              onChange={(e) => setMemoryFilter(e.target.value)}
            />
          </div>

          <div className="flex-col gap-2" style={{ flex: '1 1 300px' }}>
            <label>再読記憶の属性フィルター</label>
            <div className="flex gap-2">
              <select 
                className="input-field"
                value={aspectFilter}
                onChange={e => setAspectFilter(e.target.value)}
                style={{ flex: 2 }}
              >
                <option value="">-- 指定なし --</option>
                {Object.entries(ASPECT_NAMES_JA).map(([k, v]) => (
                  <option key={k} value={k}>{ASPECT_ICONS[k]} {v}</option>
                ))}
              </select>
              <input 
                type="number" 
                className="input-field" 
                value={aspectMinVal}
                onChange={e => setAspectMinVal(parseInt(e.target.value) || 1)}
                min={1}
                style={{ flex: 1 }}
                disabled={!aspectFilter}
                title="指定値以上"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 mt-4" style={{ flex: '1 1 100%' }}>
            <label className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={onlyOwned}
                onChange={e => setOnlyOwned(e.target.checked)}
                style={{ transform: 'scale(1.2)' }}
              />
              所持している本だけ表示する
            </label>
          </div>
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
        {filteredBooks.map(b => {
          const memAspects = getMemoryAspects(b.memory_on_reread);
          
          return (
            <div key={b.id} className="glass-panel p-4 flex-col justify-between" style={{ border: (inventory[b.id] || 0) > 0 ? '1px solid var(--primary)' : undefined }}>
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h3 style={{ fontSize: '1.1em', lineHeight: '1.3' }}>
                    📖 {formatItemName(b)}
                  </h3>
                  <input 
                    type="checkbox" 
                    checked={(inventory[b.id] || 0) > 0}
                    onChange={e => handleInventoryChange(b.id, e.target.checked ? 1 : 0)}
                    style={{ transform: 'scale(1.5)', margin: '4px' }}
                  />
                </div>
                
                <div className="text-muted mb-2" style={{ fontSize: '0.9em' }}>
                  <div className="flex-col gap-1 mb-2 p-2" style={{ background: 'rgba(0,0,0,0.03)', borderRadius: '6px' }}>
                    <div className="flex items-center gap-2">
                      <strong>再読記憶:</strong> 
                      {b.memory_name_ja ? (
                        <span style={{ color: 'var(--text-main)' }}>💭 {formatItemName({name_ja: b.memory_name_ja, name_en: b.memory_name_en || ''})}</span>
                      ) : (
                        <span>なし</span>
                      )}
                    </div>
                    {memAspects && Object.keys(memAspects).length > 0 && (
                      <div className="flex gap-2 flex-wrap mt-1">
                        {Object.entries(memAspects).map(([asp, val]) => (
                          <span key={asp} style={{ fontSize: '0.9em' }}>
                            {ASPECT_ICONS[asp]} {ASPECT_NAMES_JA[asp]}+{val}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-4 px-1">
                    <div>
                      <strong>難度:</strong> {b.difficulty_aspect ? `${ASPECT_ICONS[b.difficulty_aspect]} ${ASPECT_NAMES_JA[b.difficulty_aspect]}${b.difficulty_value}` : 'なし'}
                    </div>
                    <div>
                      <strong>言語:</strong> {b.language || 'なし'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-2 text-right">
                <a href={b.source_url} target="_blank" rel="noreferrer" style={{ fontSize: '0.8em', color: 'var(--primary-hover)', textDecoration: 'none' }}>
                  出典を開く ↗
                </a>
              </div>
            </div>
          )
        })}
        {filteredBooks.length === 0 && (
          <div className="text-muted p-4">条件に一致する本が見つかりません。</div>
        )}
      </div>
    </div>
  );
};

export default BooksMode;
