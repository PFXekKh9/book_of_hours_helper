import { useState } from 'react';
import { Calculator, Book, Info, Library, Hammer } from 'lucide-react';
import CalculatorMode from './components/CalculatorMode';
import DictionaryMode from './components/DictionaryMode';
import BooksMode from './components/BooksMode';
import CraftingMode from './components/CraftingMode';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('calculator');

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div>
          <h2 className="text-gradient mb-4">Book of Hours</h2>
          <div className="text-muted" style={{ fontSize: '0.9em' }}>支援者計算機</div>
        </div>
        
        <div className="flex-col gap-2 mt-4">
          <div 
            className={`nav-item ${activeTab === 'calculator' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculator')}
          >
            <Calculator size={20} />
            <span>計算機モード</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'dictionary' ? 'active' : ''}`}
            onClick={() => setActiveTab('dictionary')}
          >
            <Book size={20} />
            <span>辞典モード</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'books' ? 'active' : ''}`}
            onClick={() => setActiveTab('books')}
          >
            <Library size={20} />
            <span>本・蔵書</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'crafting' ? 'active' : ''}`}
            onClick={() => setActiveTab('crafting')}
          >
            <Hammer size={20} />
            <span>何が作れる？</span>
          </div>
        </div>
        
        <div style={{ marginTop: 'auto' }}>
          <div className="glass-panel p-4" style={{ fontSize: '0.75em', opacity: 0.8 }}>
            <div className="flex items-center gap-2 mb-2">
              <Info size={14} />
              <strong>免責事項・出典</strong>
            </div>
            <p>このツールは非公式のBook of Hours攻略補助ツールです。<br/>Book of Hoursおよび関連名称はWeather Factoryの所有物です。</p>
            <p className="mt-2">攻略データの一部は <a href="https://book-of-hours.fandom.com/" target="_blank" rel="noreferrer" style={{color: 'var(--primary-hover)'}}>Book of Hours Wiki on Fandom</a> の情報を参考にしています。<br/>Wiki本文は CC BY-SA 3.0 の下で提供されています。</p>
            <p className="mt-2">License: CC BY-SA 3.0</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeTab === 'calculator' && <CalculatorMode />}
        {activeTab === 'dictionary' && <DictionaryMode />}
        {activeTab === 'books' && <BooksMode />}
        {activeTab === 'crafting' && <CraftingMode />}
      </div>
    </div>
  );
}

export default App;
