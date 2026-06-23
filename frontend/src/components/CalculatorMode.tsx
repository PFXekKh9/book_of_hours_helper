import React, { useEffect, useState, useMemo } from 'react';
import type { Item, Assistant } from '../data';
import { fetchItems, fetchAssistants, ASPECT_ICONS, ASPECT_NAMES_JA, formatItemName } from '../data';
const CalculatorMode: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  
  const [targetValue, setTargetValue] = useState(5);
  const [targetAspect, setTargetAspect] = useState('edge');
  const [selectedAssistant, setSelectedAssistant] = useState('');
  const [inventory, setInventory] = useState<Record<string, number>>({});
  const [hideZero, setHideZero] = useState(false);
  
  useEffect(() => {
    fetchItems().then(setItems);
    fetchAssistants().then(setAssistants);
  }, []);

  const handleInventoryChange = (id: string, val: number) => {
    setInventory(prev => ({ ...prev, [id]: Math.max(0, val) }));
  };

  // Computation
  const assistantVal = selectedAssistant ? (assistants.find(a => a.id === selectedAssistant)?.aspects[targetAspect] || 0) : 0;
  
  const selectedItems = items.filter(item => (inventory[item.id] || 0) > 0 && item.aspects[targetAspect] > 0);
  
  const totalValue = assistantVal + selectedItems.reduce((acc, item) => acc + (item.aspects[targetAspect] || 0), 0);
  const diff = targetValue - totalValue;

  const consumedItems = selectedItems.filter(i => i.consumed);
  const nonConsumedItems = selectedItems.filter(i => !i.consumed);
  const rareCount = selectedItems.filter(i => i.rarity === 'rare' || i.rarity === 'limited').length;
  const craftCount = selectedItems.filter(i => i.craft).length;

  const isSuccess = totalValue >= targetValue;

  // Find Candidates if lacking
  const candidateItems = useMemo(() => {
    if (isSuccess || diff <= 0) return [];
    return items
      .filter(i => (inventory[i.id] || 0) === 0 && (i.aspects[targetAspect] || 0) > 0)
      .sort((a, b) => (b.aspects[targetAspect] || 0) - (a.aspects[targetAspect] || 0))
      .slice(0, 5);
  }, [items, inventory, targetAspect, diff, isSuccess]);

  return (
    <div>
      <h2 className="mb-4 text-gradient">支援者計算機</h2>
      
      <div className="glass-panel p-6 mb-6">
        <h3 className="mb-4">1. 目標設定</h3>
        <div className="flex gap-4">
          <div className="flex-col gap-2" style={{ flex: 1 }}>
            <label>対象属性</label>
            <select 
              className="input-field"
              value={targetAspect}
              onChange={e => setTargetAspect(e.target.value)}
            >
              {Object.entries(ASPECT_NAMES_JA).map(([k, v]) => (
                <option key={k} value={k}>{ASPECT_ICONS[k]} {v}</option>
              ))}
            </select>
          </div>
          <div className="flex-col gap-2" style={{ flex: 1 }}>
            <label>目標値</label>
            <input 
              type="number" 
              className="input-field" 
              value={targetValue}
              onChange={e => setTargetValue(parseInt(e.target.value) || 0)}
              min={1}
            />
          </div>
        </div>

        <div className="flex-col gap-2 mt-4">
          <label>支援者 (初期値)</label>
          <select 
            className="input-field"
            value={selectedAssistant}
            onChange={e => setSelectedAssistant(e.target.value)}
          >
            <option value="">-- なし --</option>
            {assistants.map(a => (
              <option key={a.id} value={a.id}>
                {formatItemName(a)} ({ASPECT_ICONS[targetAspect]} {a.aspects[targetAspect] || 0})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="glass-panel p-6 mb-6" style={{ border: isSuccess ? '1px solid var(--success, #0d8636)' : '1px solid var(--border)' }}>
        <h3 className="mb-4">2. 計算結果</h3>
        <div className="flex justify-between items-center mb-4">
          <div style={{ fontSize: '1.2em' }}>
            合計値: <strong style={{ color: isSuccess ? '#11b448' : '#fe5267', fontSize: '1.5em' }}>{totalValue}</strong> / {targetValue}
          </div>
          <div className="flex gap-4 text-muted" style={{ fontSize: '0.9em' }}>
            <span>消費アイテム: {consumedItems.length}</span>
            <span>レア: {rareCount}</span>
            <span>クラフト品: {craftCount}</span>
          </div>
        </div>

        {isSuccess ? (
          <div style={{ color: '#11b448', fontWeight: 'bold', marginBottom: '16px' }}>
            ✅ 目標値に到達しました！
          </div>
        ) : (
          <div style={{ color: '#fe5267', fontWeight: 'bold', marginBottom: '16px' }}>
            ❌ あと {diff} 足りません。
          </div>
        )}

        {!isSuccess && candidateItems.length > 0 && (
          <div className="mb-4 p-4" style={{ background: 'rgba(254, 82, 103, 0.1)', borderRadius: '8px' }}>
            <strong>追加候補アイテム:</strong>
            <ul style={{ paddingLeft: '20px', marginTop: '8px' }}>
              {candidateItems.map(c => (
                <li key={c.id}>
                  {formatItemName(c)} ({ASPECT_ICONS[targetAspect]} +{c.aspects[targetAspect]}) 
                  {c.how_to_get && c.how_to_get.length > 0 ? ` - ${c.how_to_get[0]}` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex gap-4 mt-4">
          <div style={{ flex: 1 }}>
            <h4 className="mb-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '4px' }}>消費されるもの</h4>
            {consumedItems.length === 0 ? <div className="text-muted">なし</div> : (
              <ul style={{ listStyle: 'none' }}>
                {consumedItems.map(i => <li key={i.id}>- {formatItemName(i)} (+{i.aspects[targetAspect]})</li>)}
              </ul>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <h4 className="mb-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '4px' }}>消費されないもの</h4>
            {nonConsumedItems.length === 0 ? <div className="text-muted">なし</div> : (
              <ul style={{ listStyle: 'none' }}>
                {nonConsumedItems.map(i => <li key={i.id}>- {formatItemName(i)} (+{i.aspects[targetAspect]})</li>)}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6">
        <div className="flex justify-between items-center mb-4">
          <h3>3. 所持アイテム選択</h3>
          <label className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={hideZero}
              onChange={e => setHideZero(e.target.checked)}
            />
            所持数0を隠す
          </label>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
          {items.map(item => {
            const aspectVal = item.aspects[targetAspect];
            if (!aspectVal) return null;
            
            const invCount = inventory[item.id] || 0;
            if (hideZero && invCount === 0) return null;
            
            return (
              <div key={item.id} className="flex justify-between items-center p-3" style={{ background: 'rgba(0,0,0,0.03)', borderRadius: '8px', border: invCount > 0 ? '1px solid var(--primary)' : '1px solid transparent' }}>
                <div className="flex-col">
                  <span>{formatItemName(item)}</span>
                  <div className="flex gap-2 items-center text-muted" style={{ fontSize: '0.8em' }}>
                    <span className="aspect-badge" style={{ padding: '2px 6px' }}>{ASPECT_ICONS[targetAspect]} +{aspectVal}</span>
                    {item.consumed ? <span style={{ color: '#fe6274' }}>消費</span> : <span style={{ color: '#11b448' }}>非消費</span>}
                  </div>
                </div>
                {item.category === 'memory' || item.category === 'soul' || item.category === 'tool' ? (
                  <input 
                    type="checkbox" 
                    checked={invCount > 0}
                    onChange={e => handleInventoryChange(item.id, e.target.checked ? 1 : 0)}
                    style={{ transform: 'scale(1.2)' }}
                  />
                ) : (
                  <input 
                    type="number" 
                    className="input-field" 
                    style={{ width: '60px', padding: '4px' }}
                    value={invCount}
                    onChange={e => handleInventoryChange(item.id, parseInt(e.target.value) || 0)}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default CalculatorMode;
