import { useState, useEffect, useMemo } from 'react';
import type { Item, MemorySource, Skill } from '../data';
import { fetchItems, fetchMemorySources, fetchSkills, fetchSkillRecipes, ASPECT_ICONS, ASPECT_NAMES_JA } from '../data';

export default function CraftingMode() {
  const [items, setItems] = useState<Item[]>([]);
  const [memorySources, setMemorySources] = useState<MemorySource[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [skillRecipes, setSkillRecipes] = useState<Record<string, string[]>>({});
  
  const [mode, setMode] = useState<'aspect' | 'skill'>('skill');
  
  // Aspect search state
  const [selectedAspect, setSelectedAspect] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<number | ''>('');

  // Skill search state
  const [selectedSkillEn, setSelectedSkillEn] = useState<string>('');
  const [skillLevel, setSkillLevel] = useState<number>(1);

  useEffect(() => {
    fetchItems().then(setItems);
    fetchMemorySources().then(setMemorySources);
    fetchSkills().then(setSkills);
    fetchSkillRecipes().then(setSkillRecipes);
  }, []);

  const craftableItemsByAspect = useMemo(() => {
    return items.filter(item => {
      if (!item.craft) return false;
      const principles = Array.isArray(item.craft.principle) ? item.craft.principle : [item.craft.principle];
      if (selectedAspect && !principles.includes(selectedAspect)) return false;
      if (selectedLevel !== '' && item.craft.level > selectedLevel) return false;
      return true;
    }).sort((a, b) => {
      if (a.craft!.level !== b.craft!.level) {
        return a.craft!.level - b.craft!.level;
      }
      const pA = Array.isArray(a.craft!.principle) ? a.craft!.principle.join(',') : a.craft!.principle;
      const pB = Array.isArray(b.craft!.principle) ? b.craft!.principle.join(',') : b.craft!.principle;
      return pA.localeCompare(pB);
    });
  }, [items, selectedAspect, selectedLevel]);

  const craftableItemsBySkill = useMemo(() => {
    if (!selectedSkillEn) return [];
    
    const skill = skills.find(s => s.name_en === selectedSkillEn);
    if (!skill) return [];

    const specificItemsEn = skillRecipes[selectedSkillEn] || [];
    
    // Total aspect point estimate:
    // Skill provides `skillLevel` points.
    // Memory provides ~2 points. Soul provides ~2 points. Total approx = skillLevel + 4
    const maxAspect = skillLevel + 4;
    
    return items.filter(item => {
      if (!item.craft) return false;
      const principles = Array.isArray(item.craft.principle) ? item.craft.principle : [item.craft.principle];
      
      // Does this skill provide the required principle?
      const hasPrinciple = principles.some(p => skill.aspects.includes(p));
      if (!hasPrinciple) return false;

      // Prentice (level 5) crafts are generic. Any skill with the aspect can craft it.
      if (item.craft.level === 5 && maxAspect >= 5) {
        return true;
      }
      
      // Scholar/Keeper crafts are specific to the skill.
      if ((item.craft.level === 10 || item.craft.level === 15) && specificItemsEn.includes(item.name_en)) {
        if (maxAspect >= item.craft.level) {
          return true;
        }
      }
      
      return false;
    }).sort((a, b) => a.craft!.level - b.craft!.level);
    
  }, [items, skills, skillRecipes, selectedSkillEn, skillLevel]);

  const renderItemCard = (item: Item) => (
    <div key={item.id} className="glass-panel p-4 card-hover" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <h3 style={{ margin: 0, color: 'var(--text-main)', fontSize: '1.2em' }}>
          {item.name_ja && item.name_ja !== item.name_en ? item.name_ja : item.name_en}
        </h3>
        <span className="aspect-badge" style={{ fontSize: '0.9em', background: 'rgba(255,255,255,0.1)' }}>
          レベル {item.craft!.level} : {(Array.isArray(item.craft!.principle) ? item.craft!.principle : [item.craft!.principle]).map((p, idx, arr) => (
            <span key={p}>
              {ASPECT_ICONS[p]} {ASPECT_NAMES_JA[p]}{idx < arr.length - 1 ? ' / ' : ''}
            </span>
          ))}
        </span>
      </div>
      
      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '4px' }}>
        {Object.entries(item.aspects).map(([asp, val]) => (
          <span key={asp} className="aspect-badge">
            {ASPECT_ICONS[asp]} {asp} +{val}
          </span>
        ))}
      </div>

      {((item.how_to_get && item.how_to_get.length > 0) || (memorySources.find(m => m.memory_id === item.id)?.books?.length || 0) > 0) && (
        <div style={{ fontSize: '0.85em', color: 'var(--text-muted)', marginTop: '8px' }}>
          <strong>詳細 / 必要なスキル:</strong>
          <ul style={{ paddingLeft: '20px', marginTop: '4px' }}>
            {(item.how_to_get || []).map((htg, i) => {
               if (htg === "対応本を再読" || htg.startsWith("特定の")) return null;
               return <li key={i}>{htg}</li>;
            })}
            {(() => {
              const ms = memorySources.find(m => m.memory_id === item.id);
              if (ms && ms.books && ms.books.length > 0) {
                return (
                  <li key="books">
                    以下の本を再読（クラフト以外でも入手可）:
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
  );

  return (
    <div className="glass-panel p-6 animate-fade-in" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h2 className="text-gradient mb-4">何が作れる？ (クラフト検索)</h2>
      
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button 
          className={`filter-chip ${mode === 'skill' ? 'active' : ''}`}
          onClick={() => setMode('skill')}
        >
          自分のスキルから提案
        </button>
        <button 
          className={`filter-chip ${mode === 'aspect' ? 'active' : ''}`}
          onClick={() => setMode('aspect')}
        >
          属性から絞り込み
        </button>
      </div>

      {mode === 'aspect' && (
        <>
          <p style={{ fontSize: '0.9em', color: 'var(--text-muted)', marginBottom: '16px' }}>
            特定の属性とレベルを指定して、作れるアイテムを検索します。
          </p>
          <div className="glass-panel p-4 mb-4" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '200px' }}>
              <label style={{ fontSize: '0.9em', color: 'var(--text-muted)' }}>属性 (Principle)</label>
              <select className="input-base" value={selectedAspect} onChange={(e) => setSelectedAspect(e.target.value)}>
                <option value="">すべて</option>
                {Object.keys(ASPECT_ICONS).map(asp => (
                  <option key={asp} value={asp}>{ASPECT_ICONS[asp]} {ASPECT_NAMES_JA[asp]} ({asp})</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '200px' }}>
              <label style={{ fontSize: '0.9em', color: 'var(--text-muted)' }}>クラフトレベル</label>
              <select className="input-base" value={selectedLevel} onChange={(e) => setSelectedLevel(e.target.value ? Number(e.target.value) : '')}>
                <option value="">すべて</option>
                <option value={5}>レベル 5 (徒弟 / Prentice)</option>
                <option value={10}>レベル 10 (学者 / Scholar)</option>
                <option value={15}>レベル 15 (番人 / Keeper)</option>
              </select>
            </div>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', paddingRight: '4px' }}>
            {craftableItemsByAspect.length === 0 ? (
              <div className="text-muted" style={{ textAlign: 'center', padding: '40px' }}>条件に一致するクラフトレシピが見つかりません。</div>
            ) : craftableItemsByAspect.map(renderItemCard)}
          </div>
        </>
      )}

      {mode === 'skill' && (
        <>
          <p style={{ fontSize: '0.9em', color: 'var(--text-muted)', marginBottom: '16px' }}>
            持っているスキルとレベルを選ぶと、「魂」や「記憶」を組み合わせた際に作れる可能性のあるアイテムを提案します。
          </p>
          <div className="glass-panel p-4 mb-4" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1, minWidth: '200px', maxWidth: '400px' }}>
              <label style={{ fontSize: '0.9em', color: 'var(--text-muted)' }}>スキル (Skill)</label>
              <select className="input-base" value={selectedSkillEn} onChange={(e) => setSelectedSkillEn(e.target.value)}>
                <option value="">スキルを選択...</option>
                {skills.sort((a, b) => {
                  const nameA = a.name_ja && a.name_ja !== a.name_en ? a.name_ja : a.name_en;
                  const nameB = b.name_ja && b.name_ja !== b.name_en ? b.name_ja : b.name_en;
                  return nameA.localeCompare(nameB);
                }).map(s => (
                  <option key={s.id} value={s.name_en}>
                    {s.name_ja && s.name_ja !== s.name_en ? s.name_ja : s.name_en} ({s.aspects.map(asp => ASPECT_NAMES_JA[asp] || asp).join(' / ')})
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '80px' }}>
              <label style={{ fontSize: '0.9em', color: 'var(--text-muted)' }}>レベル</label>
              <input 
                type="number" 
                min={1} max={9} 
                className="input-base" 
                value={skillLevel} 
                onChange={(e) => setSkillLevel(Number(e.target.value))}
                style={{ width: '100%', textAlign: 'center' }}
              />
            </div>
          </div>
          
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', paddingRight: '4px' }}>
            {!selectedSkillEn ? (
              <div className="text-muted" style={{ textAlign: 'center', padding: '40px' }}>スキルを選択してください。</div>
            ) : craftableItemsBySkill.length === 0 ? (
              <div className="text-muted" style={{ textAlign: 'center', padding: '40px' }}>このスキルで作れるアイテムが見つかりません。</div>
            ) : (
              <>
                <div style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '0.95em', background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '8px' }}>
                  <strong>見込み合計属性値: {skillLevel + 4}</strong> <span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>（スキル {skillLevel} ＋ 魂/記憶など約4）</span><br/>
                  <span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>※ クラフトは合計属性値が <strong>5（徒弟）、10（学者）、15（番人）</strong> に達した時に解禁されます。レベルを上げてもこの境界線を越えなければ、作れるものは増えません。</span>
                </div>
                {craftableItemsBySkill.map(renderItemCard)}
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
