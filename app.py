from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

import streamlit as st


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "items.json"

ASPECTS = [
    "edge", "forge", "lantern", "grail", "heart", "moth", "knock", 
    "winter", "moon", "sky", "scale", "rose", "nectar",
]

ASPECT_LABELS = {
    "edge": "⚔️ edge / 刃",
    "forge": "🔥 forge / 鍛造",
    "lantern": "🏮 lantern / 灯",
    "grail": "🍷 grail / 杯",
    "heart": "❤️ heart / 心臓",
    "moth": "🦋 moth / 蛾",
    "knock": "🗝️ knock / 鍵",
    "winter": "❄️ winter / 冬",
    "moon": "🌙 moon / 月",
    "sky": "☁️ sky / 空",
    "scale": "🐍 scale / 鱗",
    "rose": "🌹 rose / 薔薇",
    "nectar": "🍯 nectar / 蜜",
}

CATEGORY_LABELS = {
    "assistant": "🤝 支援者",
    "soul": "💠 魂・精神",
    "memory": "💭 記憶",
    "food": "🍞 食べ物",
    "drink": "🍷 飲み物",
    "tool": "🔨 道具",
    "special": "✨ 特殊",
}

ASPECT_SHORT_LABELS = {
    "edge": "⚔️刃", "forge": "🔥鍛造", "lantern": "💡灯", "grail": "🍷杯",
    "heart": "❤️心臓", "moth": "🦋蛾", "knock": "🗝️鍵", "winter": "❄️冬",
    "moon": "🌙月", "sky": "🌬️空", "scale": "🐍鱗", "rose": "🌹薔薇",
    "nectar": "🍯蜜",
}

OPTIONAL_CATEGORIES = ["soul", "memory", "food", "drink", "tool", "special"]


def load_data() -> dict[str, list[dict[str, Any]]]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def aspect_format(aspect: str, value: int) -> str:
    return f"{ASPECT_LABELS.get(aspect, aspect)} +{value}"


def item_label(item: dict[str, Any], target_aspect: str | None = None) -> str:
    value = ""
    if target_aspect:
        aspect_value = item.get("aspects", {}).get(target_aspect, 0)
        if aspect_value:
            value = f" / {aspect_format(target_aspect, aspect_value)}"
    return f"{item['name_ja']} / {item['name_en']}{value}"

def full_item_label(item: dict[str, Any]) -> str:
    aspect_parts = []
    for aspect in ASPECTS:
        val = item.get("aspects", {}).get(aspect, 0)
        if val > 0:
            short_label = ASPECT_SHORT_LABELS.get(aspect, aspect)
            aspect_parts.append(f"{short_label}+{val}")
    aspect_str = " ".join(aspect_parts)
    prefix = "💠 " if item.get("category") == "soul" else ""
    return f"{prefix}{item['name_ja']} / {item['name_en']}　{aspect_str}"


def aspects_text(aspects: dict[str, int]) -> str:
    if not aspects:
        return "-"
    parts = []
    for aspect in ASPECTS:
        value = aspects.get(aspect, 0)
        if value:
            parts.append(aspect_format(aspect, value))
    return ", ".join(parts)


def get_aspect_value(item: dict[str, Any], aspect: str) -> int:
    return int(item.get("aspects", {}).get(aspect, 0))


def group_items_by_category(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {category: [] for category in OPTIONAL_CATEGORIES}
    for item in items:
        category = item.get("category")
        if category in grouped:
            grouped[category].append(item)
    return grouped


def calculate_combinations(
    assistant: dict[str, Any],
    available_items: list[dict[str, Any]],
    target_aspect: str,
    target_value: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped = group_items_by_category(available_items)

    category_choices: list[list[dict[str, Any] | None]] = []
    for category in OPTIONAL_CATEGORIES:
        category_choices.append([None] + grouped[category])

    results: list[dict[str, Any]] = []
    best = {
        "total": get_aspect_value(assistant, target_aspect),
        "items": [assistant],
        "consumed": [],
        "not_consumed": [assistant],
    }

    for choices in itertools.product(*category_choices):
        selected_items = [assistant] + [item for item in choices if item is not None]
        total = sum(get_aspect_value(item, target_aspect) for item in selected_items)

        consumed = [item for item in selected_items if item.get("consumed", False)]
        not_consumed = [item for item in selected_items if not item.get("consumed", False)]

        result = {
            "total": total,
            "items": selected_items,
            "consumed": consumed,
            "not_consumed": not_consumed,
        }

        if total > best["total"]:
            best = result

        if total >= target_value:
            results.append(result)

    results.sort(
        key=lambda r: (
            abs(r["total"] - target_value),
            len(r["consumed"]),
            sum(1 for i in r["items"] if i.get("rarity") == "rare"),
            sum(1 for i in r["items"] if i.get("recipe")),
            r["total"],
        )
    )
    return results, best


def render_item_table(items: list[dict[str, Any]], target_aspect: str) -> None:
    rows = []
    for item in items:
        rows.append(
            {
                "カテゴリ": CATEGORY_LABELS.get(item["category"], item["category"]),
                "名前": f"{item['name_ja']} / {item['name_en']}",
                f"{target_aspect}値": get_aspect_value(item, target_aspect),
                "全要素": aspects_text(item.get("aspects", {})),
                "消費": "はい" if item.get("consumed", False) else "いいえ",
                "必要数": 1 if item.get("consumed", False) else "-",
                "メモ": item.get("notes", ""),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_result_card(result: dict[str, Any], target_aspect: str, target_value: int, index: int) -> None:
    over = result["total"] - target_value
    title = f"#{index} 合計 {result['total']} / 目標 {target_value}"
    if over > 0:
        title += f"（+{over}）"

    rare_count = sum(1 for i in result["items"] if i.get("rarity") == "rare")
    craft_count = sum(1 for i in result["items"] if i.get("recipe"))

    with st.expander(title, expanded=index <= 5):
        st.markdown(f"**合計値**: {result['total']} / **目標値**: {target_value}")
        st.markdown(f"**消費アイテム数**: {len(result['consumed'])} / **レアアイテム数**: {rare_count} / **クラフト品数**: {craft_count}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**消費されるもの一覧**")
            if result["consumed"]:
                for item in result["consumed"]:
                    st.write(f"- {full_item_label(item)}")
            else:
                st.write("- なし")

        with col2:
            st.markdown("**消費されないもの一覧**")
            if result["not_consumed"]:
                for item in result["not_consumed"]:
                    st.write(f"- {full_item_label(item)}")
            else:
                st.write("- なし")

        with st.expander("入手方法 / アイテム詳細"):
            for item in result["items"]:
                if item["category"] == "assistant":
                    continue
                st.markdown(f"**{item['name_ja']}** ({CATEGORY_LABELS.get(item['category'], item['category'])})")
                
                details = []
                if item.get("rarity") and item["rarity"] != "common":
                    details.append(f"**レア度**: {item['rarity']}")
                if item.get("tags"):
                    details.append(f"**タグ**: {', '.join(item['tags'])}")
                if item.get("persistent"):
                    details.append("**特性**: 持続記憶 (夜明けで消滅しない)")
                if item.get("obtain_type"):
                    details.append(f"**入手種別**: {', '.join(item['obtain_type'])}")
                if item.get("how_to_get"):
                    details.append("**入手方法**:\n" + "\n".join(f"  - {h}" for h in item["how_to_get"]))
                if item.get("locations"):
                    details.append("**場所**:\n" + "\n".join(f"  - {l}" for l in item["locations"]))
                if item.get("craft"):
                    craft = item["craft"]
                    if isinstance(craft, dict):
                        principles = craft.get('principle', [])
                        if isinstance(principles, str): principles = [principles]
                        p_str = 'または'.join(ASPECT_LABELS.get(p, p).split(' / ')[-1] for p in principles)
                        details.append(f"**クラフト条件**: {p_str} {craft.get('level', '')}")
                    else:
                        details.append(f"**クラフト条件**: {craft}")
                if item.get("recipe"):
                    rec = item["recipe"]
                    rec_str = ", ".join(f"{k}: {v}" for k, v in rec.items()) if isinstance(rec, dict) else str(rec)
                    details.append(f"**レシピ**: {rec_str}")
                    
                if details:
                    st.markdown("\n\n".join(details))
                else:
                    st.write("詳細データなし")
                st.divider()


def render_calculator_mode(data: dict[str, Any]) -> None:
    st.title("🧮 Book of Hours 支援者計算機")
    st.caption("支援者にアイテムを組み合わせて、目標要素値に届く組み合わせを探します。")

    assistants = data["assistants"]
    items = data["items"]

    with st.sidebar:
        st.header("条件")
        assistant = st.selectbox(
            "支援者",
            assistants,
            format_func=lambda item: item_label(item),
        )

        target_aspect = st.selectbox(
            "目標要素",
            ASPECTS,
            index=ASPECTS.index("moth"),
            format_func=lambda aspect: ASPECT_LABELS.get(aspect, aspect),
        )

        target_value = st.number_input("必要値", min_value=1, max_value=99, value=10, step=1)
        max_results = st.number_input("表示する最大件数", min_value=1, max_value=500, value=50, step=10, help="条件を満たす組み合わせが多い場合、上位だけ表示します。")

        st.header("フィルター")
        filter_no_consumed = st.checkbox("消費アイテムを避ける", value=False)
        filter_no_rare = st.checkbox("レア品を避ける", value=False)
        filter_no_crafted = st.checkbox("クラフト品を避ける", value=False)
        filter_exclude_numa = st.checkbox("ヌマ限定を除外する", value=True)

    st.subheader("1. 所持アイテム")
    st.write("持っているものを設定してください。カテゴリごとに最大1つまで使う前提で計算します。")
    
    hide_unowned = st.checkbox("所持数0のアイテムを非表示", value=False)

    selected_item_info: dict[str, int] = {}
    grouped = group_items_by_category(items)

    tabs = st.tabs([CATEGORY_LABELS[category] for category in OPTIONAL_CATEGORIES])
    for tab, category in zip(tabs, OPTIONAL_CATEGORIES):
        with tab:
            category_items = grouped[category]
            if not category_items:
                st.info("このカテゴリのデータはありません。")
                continue

            cols = st.columns(2)
            rendered_count = 0
            for item in category_items:
                widget_key = f"owned_{item['id']}"
                current_val = st.session_state.get(widget_key)
                if current_val is None:
                    current_val = 0
                elif isinstance(current_val, bool):
                    current_val = 1 if current_val else 0

                if hide_unowned and current_val == 0:
                    continue

                with cols[rendered_count % 2]:
                    
                    extra_help = []
                    if item.get('persistent'): extra_help.append("持続記憶")
                    if item.get('obtain_type'): extra_help.append(f"入手種別: {', '.join(item['obtain_type'])}")
                    extra_text = f"\n\n" + "\n".join(extra_help) + "\n" if extra_help else ""

                    help_text = (
                        f"カテゴリ: {CATEGORY_LABELS.get(item['category'], item['category'])}\n\n"
                        f"要素: {aspects_text(item.get('aspects', {}))}\n\n"
                        f"消費: {'はい' if item.get('consumed', False) else 'いいえ'}"
                        f"{extra_text}\n"
                        f"メモ: {item.get('notes', '')}"
                    )
                    
                    is_numeric = item["category"] in ["food", "drink", "memory", "special"]
                    
                    if is_numeric:
                        owned_count = st.number_input(
                            full_item_label(item),
                            min_value=0,
                            value=current_val,
                            key=widget_key,
                            help=help_text
                        )
                        selected_item_info[item["id"]] = owned_count
                    else:
                        checked = st.checkbox(
                            full_item_label(item),
                            value=bool(current_val),
                            key=widget_key,
                            help=help_text
                        )
                        selected_item_info[item["id"]] = 1 if checked else 0
                rendered_count += 1
            
            if rendered_count == 0 and hide_unowned:
                st.info("表示するアイテムがありません。「所持数0のアイテムを非表示」のチェックを外すと追加できます。")

    available_items = []
    for item in items:
        if filter_no_consumed and item.get("consumed"): continue
        if filter_no_rare and item.get("rarity") == "rare": continue
        if filter_no_crafted and item.get("recipe"): continue
        if filter_exclude_numa and "numa" in item.get("tags", []): continue
        
        owned_count = selected_item_info.get(item["id"], 0)
        if owned_count == 0:
            continue
            
        available_items.append(item)

    st.divider()
    st.subheader("2. 計算")

    assistant_base = get_aspect_value(assistant, target_aspect)
    st.write(
        f"選択中の支援者: **{item_label(assistant)}** / "
        f"{target_aspect} 基礎値: **{assistant_base}**"
    )

    if st.button("計算", type="primary"):
        results, best = calculate_combinations(
            assistant=assistant,
            available_items=available_items,
            target_aspect=target_aspect,
            target_value=int(target_value),
        )

        if results:
            st.success(f"{len(results)}件の組み合わせが見つかりました。")
            shown_results = results[: int(max_results)]

            if len(results) > len(shown_results):
                st.info(f"組み合わせが多いため、上位{len(shown_results)}件だけ表示します。")

            for i, result in enumerate(shown_results, start=1):
                render_result_card(result, target_aspect, int(target_value), i)
        else:
            shortage = int(target_value) - best["total"]
            st.error("目標値に届く組み合わせはありません。")
            st.metric("現在の最大値", best["total"])
            st.metric("不足値", shortage)

            st.markdown("**最大値になる組み合わせ**")
            render_item_table(best["items"], target_aspect)

            st.markdown("**追加候補**")
            candidates = []
            best_by_cat = {cat: None for cat in OPTIONAL_CATEGORIES}
            for b_item in best["items"]:
                if b_item.get("category") in best_by_cat:
                    best_by_cat[b_item["category"]] = b_item

            for cat in OPTIONAL_CATEGORIES:
                current_val = get_aspect_value(best_by_cat[cat], target_aspect) if best_by_cat[cat] else 0
                for item in items:
                    if item.get("category") == cat:
                        if filter_no_consumed and item.get("consumed"): continue
                        if filter_no_rare and item.get("rarity") == "rare": continue
                        if filter_no_crafted and item.get("recipe"): continue
                        if filter_exclude_numa and "numa" in item.get("tags", []): continue
                        
                        val = get_aspect_value(item, target_aspect)
                        gain = val - current_val
                        if gain >= shortage:
                            candidates.append(f"{item['name_ja']} (+{gain})")
            
            if candidates:
                st.write(f"あと **+{shortage}**。以下のアイテムを入手・使用すれば届きます：")
                st.write("、".join(candidates))
            else:
                st.write("条件内で目標に届く候補アイテムは見つかりませんでした。")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**消費されるもの**")
                if best["consumed"]:
                    for item in best["consumed"]:
                        st.write(f"- {full_item_label(item)}")
                else:
                    st.write("- なし")
            with col2:
                st.markdown("**消費されないもの**")
                if best["not_consumed"]:
                    for item in best["not_consumed"]:
                        st.write(f"- {full_item_label(item)}")
                else:
                    st.write("- なし")


def render_dictionary_mode(data: dict[str, Any]) -> None:
    st.title("📖 Book of Hours アイテム辞典")
    st.caption("すべてのアイテム・支援者の情報を検索できます。未所持のアイテムも確認可能です。")
    
    search_query = st.text_input("名前やタグで検索", "")
    
    col1, col2 = st.columns(2)
    with col1:
        cat_filter = st.multiselect("カテゴリ", [CATEGORY_LABELS[c] for c in CATEGORY_LABELS.keys()])
    with col2:
        aspect_filter = st.multiselect("要素", [ASPECT_LABELS[a] for a in ASPECTS])
    
    items = data["assistants"] + data["items"]
    
    filtered = []
    for item in items:
        if search_query:
            q = search_query.lower()
            if q not in item["name_ja"].lower() and q not in item["name_en"].lower() and q not in "".join(item.get("tags", [])).lower():
                continue
                
        if cat_filter:
            c_label = CATEGORY_LABELS.get(item["category"], item["category"])
            if c_label not in cat_filter:
                continue
                
        if aspect_filter:
            item_aspect_labels = [ASPECT_LABELS[a] for a in item.get("aspects", {}).keys()]
            if not any(a in aspect_filter for a in item_aspect_labels):
                continue
                
        filtered.append(item)
        
    st.success(f"{len(filtered)}件見つかりました。")
    
    for item in filtered:
        with st.container():
            st.subheader(f"{item['name_ja']} / {item['name_en']}")
            
            c1, c2, c3 = st.columns(3)
            c1.write(f"**カテゴリ**: {CATEGORY_LABELS.get(item['category'], item['category'])}")
            c2.write(f"**消費**: {'はい' if item.get('consumed') else 'いいえ'}")
            c3.write(f"**要素**: {aspects_text(item.get('aspects', {}))}")
            
            details = []
            if item.get("rarity") and item["rarity"] != "common":
                details.append(f"**レア度**: {item['rarity']}")
            if item.get("tags"):
                details.append(f"**タグ**: {', '.join(item['tags'])}")
            if item.get("persistent"):
                details.append("**特性**: 持続記憶 (夜明けで消滅しない)")
            if item.get("obtain_type"):
                details.append(f"**入手種別**: {', '.join(item['obtain_type'])}")
            if item.get("how_to_get"):
                details.append("**入手方法**:\n" + "\n".join(f"  - {h}" for h in item["how_to_get"]))
            if item.get("locations"):
                details.append("**場所**:\n" + "\n".join(f"  - {l}" for l in item["locations"]))
            if item.get("craft"):
                craft = item["craft"]
                if isinstance(craft, dict):
                    principles = craft.get('principle', [])
                    if isinstance(principles, str): principles = [principles]
                    p_str = 'または'.join(ASPECT_LABELS.get(p, p).split(' / ')[-1] for p in principles)
                    details.append(f"**クラフト条件**: {p_str} {craft.get('level', '')}")
                else:
                    details.append(f"**クラフト条件**: {craft}")
            if item.get("recipe"):
                rec = item["recipe"]
                rec_str = ", ".join(f"{k}: {v}" for k, v in rec.items()) if isinstance(rec, dict) else str(rec)
                details.append(f"**レシピ**: {rec_str}")
            if item.get("notes"):
                details.append(f"**メモ**: {item['notes']}")
                
            if details:
                st.markdown("\n\n".join(details))
            st.divider()



def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Noto+Sans+JP:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif !important;
    }
    
    .stApp {
        background: radial-gradient(circle at top left, #fcfaf8 0%, #f0ede9 100%);
        color: #2c3e50;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Modern expander styling */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    div[data-testid="stExpander"]:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(168, 139, 236, 0.4) !important;
        box-shadow: 0 8px 25px rgba(168, 139, 236, 0.15);
    }
    
    /* Button styling */
    button[kind="primary"] {
        background: linear-gradient(135deg, #a88bec 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(118, 75, 162, 0.3) !important;
    }
    
    /* Fancy titles */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #764ba2, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    
    /* Dataframes and text */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 8px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    </style>
    """, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Book of Hours 支援者計算機",
        page_icon="📚",
        layout="wide",
    )

    load_custom_css()
    data = load_data()
    
    with st.sidebar:
        mode = st.radio("モード切替", ["🧮 計算機", "📖 辞典"])
        st.divider()
        st.markdown("""
        <div style="font-size: 0.8em; opacity: 0.8;">
        <strong>免責事項・出典</strong><br>
        このツールは非公式のBook of Hours攻略補助ツールです。<br>
        Book of Hoursおよび関連名称はWeather Factoryの所有物です。<br><br>
        攻略データの一部は <a href="https://book-of-hours.fandom.com/" target="_blank">Book of Hours Wiki on Fandom</a> の情報を参考にしています。<br>
        Wiki本文は CC BY-SA 3.0 の下で提供されています。<br>
        このツール内の攻略データは、Wiki由来部分を含むため CC BY-SA 3.0 として提供します。<br><br>
        Source: Book of Hours Wiki, Fandom<br>
        License: CC BY-SA 3.0<br>
        Changes: 日本語化、構造化、要約、検索・計算用データへの変換
        </div>
        """, unsafe_allow_html=True)
        
    if mode == "🧮 計算機":
        render_calculator_mode(data)
    else:
        render_dictionary_mode(data)

if __name__ == "__main__":
    main()
