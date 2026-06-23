export interface AspectMap {
  [key: string]: number;
}

export interface CraftInfo {
  principle: string | string[];
  level: number;
}

export interface Item {
  id: string;
  name_ja: string;
  name_en: string;
  category: string;
  aspects: AspectMap;
  consumed: boolean;
  persistent?: boolean;
  rarity?: string;
  obtain_type?: string[];
  how_to_get?: string[];
  notes?: string;
  craft?: CraftInfo;
}

export interface Assistant {
  id: string;
  name_ja: string;
  name_en: string;
  aspects: AspectMap;
  special_categories: string[];
}

export const ASPECT_ICONS: Record<string, string> = {
  edge: "⚔️",
  forge: "🔨",
  lantern: "💡",
  grail: "🍷",
  heart: "🥁",
  moth: "🦋",
  knock: "🗝️",
  winter: "❄️",
  moon: "🌙",
  sky: "🌬️",
  scale: "🦎",
  rose: "🌹",
  nectar: "🩸"
};

export const ASPECT_NAMES_JA: Record<string, string> = {
  edge: "刃",
  forge: "炉",
  lantern: "灯",
  grail: "聖杯",
  heart: "心",
  moth: "蛾",
  knock: "開門",
  winter: "冬",
  moon: "月",
  sky: "空",
  scale: "鱗",
  rose: "薔薇",
  nectar: "蜜"
};

export const CATEGORY_LABELS: Record<string, string> = {
  assistant: "🤝 支援者",
  soul: "💠 魂・精神",
  memory: "💭 記憶",
  food: "🍞 食べ物",
  drink: "🍷 飲み物",
  tool: "🛠️ 道具",
  special: "✨ 特殊素材"
};

export async function fetchItems(): Promise<Item[]> {
  const res = await fetch(`/data/items.json?v=${Date.now()}`);
  const data = await res.json();
  return data.items;
}

export async function fetchAssistants(): Promise<Assistant[]> {
  const res = await fetch(`/data/assistants.json?v=${Date.now()}`);
  const data = await res.json();
  return data.assistants;
}

export const formatItemName = (item: {name_ja?: string, name_en: string}) => {
  return item.name_ja && item.name_ja !== item.name_en 
    ? item.name_ja
    : item.name_en;
};

export interface Book {
  id: string;
  name_ja: string;
  name_en: string;
  category: string;
  difficulty_aspect: string | null;
  difficulty_value: number | null;
  language: string | null;
  memory_on_reread: string | null;
  memory_name_ja: string | null;
  memory_name_en: string | null;
  lessons: string[];
  aspects: AspectMap;
  source_url: string;
  notes: string;
  needs_review: boolean;
  owned_count: number;
}

export interface MemorySource {
  memory_id: string;
  memory_name_ja: string | null;
  memory_name_en: string | null;
  aspects: AspectMap;
  books: {
    book_id: string;
    name_ja: string;
    name_en: string;
    difficulty_aspect: string | null;
    difficulty_value: number | null;
    language: string | null;
    source_url: string;
  }[];
}

export async function fetchBooks(): Promise<Book[]> {
  const res = await fetch(`/data/books.json?v=${Date.now()}`);
  return await res.json();
}

export async function fetchMemorySources(): Promise<MemorySource[]> {
  const res = await fetch(`/data/memory_sources.json?v=${Date.now()}`);
  return await res.json();
}

export interface Skill {
  id: string;
  name_en: string;
  name_ja: string;
  aspects: string[];
}

export async function fetchSkills(): Promise<Skill[]> {
  const res = await fetch(`/data/skills.json?v=${Date.now()}`);
  const data = await res.json();
  return data.skills;
}

export async function fetchSkillRecipes(): Promise<Record<string, string[]>> {
  const res = await fetch(`/data/skill_recipes.json?v=${Date.now()}`);
  return await res.json();
}
