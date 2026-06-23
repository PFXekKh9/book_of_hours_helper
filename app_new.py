from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

import streamlit as st


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "items.json"

ASPECTS = [
    "edge",
    "forge",
    "lantern",
    "grail",
    "heart",
    "moth",
    "knock",
    "winter",
    "moon",
    "sky",
    "scale",
    "rose",
    "nectar",
]

ASPECT_LABELS = {
    "edge": "edge / 刃",
    "forge": "forge / 鍛造",
    "lantern": "lantern / 灯",
    "grail": "grail / 杯",
    "heart": "heart / 心臓",
    "moth": "moth / 蛾",
    "knock": "knock / 鍵",
    "winter": "winter / 冬",
    "moon": "moon / 月",
    "sky": "sky / 空",
    "scale": "scale / 鱗",
    "rose": "rose / 薔薇",
    "nectar": "nectar / 蜜",
}

CATEGORY_LABELS = {
    "assistant": "支援者",
    "soul": "魂",
    "memory": "記憶",
    "food": "食べ物",
    "drink": "飲み物",
    "tool": "道具",
    "special": "特殊",
}

OPTIONAL_CATEGORIES = ["soul", "memory", "food", "drink", "tool", "special"]


@st.cache_data
def load_data() -> dict[str, list[dict[str, Any]]]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def item_label(item: dict[str, Any], target_aspect: str | None = None) -> str:
    value = ""
    if target_aspect:
        aspect_value = item.get("aspects", {}).get(target_aspect, 0)
        value = f" / {target_aspect}+{aspect_value}" if aspect_value else ""
    return f"{item['name_ja']} / {item['name_en']}{value}"


def aspects_text(aspects: dict[str, int]) -> str:
    if not aspects:
        return "-"
    parts = []
    for aspect in ASPECTS:
        value = aspects.get(aspect, 0)
        if value:
            parts.append(f"{aspect} {value}")
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
    """カテゴリごと最大1つの制限を守って全組み合わせを計算する。"""
    grouped = group_items_by_category(available_items)

    category_choices: list[list[dict[str, Any] | None]] = []
    for category in OPTIONAL_CATEGORIES:
        # Noneは「そのカテゴリを使わない」という選択肢
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

    # 見やすさ優先:
    # 1. 合計値が低い順。過剰投入が少ないものを先に出す。
    # 2. アイテム数が少ない順。
    # 3. 消費アイテム数が少ない順。
    results.sort(
        key=lambda r: (
            abs(r["total"] - target_value), # 目標値との差が少ない
            len(r["consumed"]),             # 消費アイテムが少ない
            sum(1 for i in r["items"] if i.get("rarity") == "rare"), # rareアイテムが少ない
            sum(1 for i in r["items"] if i.get("recipe")),           # クラフト品が少ない
            r["total"],                     # 合計値が高すぎない
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
                "メモ": item.get("notes", ""),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_result_card(result: dict[str, Any], target_aspect: str, target_value: int, index: int) -> None:
    over = result["total"] - target_value
    title = f"#{index} 合計 {result['total']} / 目標 {target_value}"
    if over > 0:
        title += f"（+{over}）"

    with st.expander(title, expanded=index <= 5):
        st.markdown("**使ったもの**")
        render_item_table(result["items"], target_aspect)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**消費されるもの**")
            if result["consumed"]:
                for item in result["consumed"]:
                    st.write(f"- {item_label(item, target_aspect)}")
            else:
                st.write("- なし")

        with col2:
            st.markdown("**消費されないもの**")
            if result["not_consumed"]:
                for item in result["not_consumed"]:
                    st.write(f"- {item_label(item, target_aspect)}")
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
                if item.get("how_to_get"):
                    details.append("**入手方法**:\n" + "\n".join(f"  - {h}" for h in item["how_to_get"]))
                if item.get("locations"):
                    details.append("**場所**:\n" + "\n".join(f"  - {l}" for l in item["locations"]))
                if item.get("recipe"):
                    rec = item["recipe"]
                    rec_str = ", ".join(f"{k}: {v}" for k, v in rec.items()) if isinstance(rec, dict) else str(rec)
                    details.append(f"**レシピ**: {rec_str}")
                    
                if details:
                    st.markdown("\n\n".join(details))
                else:
                    st.write("詳細データなし")
                st.divider()


def main() -> None:
    st.set_page_config(
        page_title="Book of Hours 支援者計算機",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Book of Hours 支援者計算機")
    st.caption("支援者に魂・記憶・食べ物・飲み物・道具・特殊を足して、目標要素値に届く組み合わせを探します。")

    data = load_data()
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

        target_value = st.number_input(
            "必要値",
            min_value=1,
            max_value=99,
            value=10,
            step=1,
        )

        max_results = st.number_input(
            "表示する最大件数",
            min_value=1,
            max_value=500,
            value=50,
            step=10,
            help="条件を満たす組み合わせが多い場合、上位だけ表示します。",
        )

    st.subheader("1. 所持アイテム")
    st.write("持っているものだけONにしてください。カテゴリごとに最大1つまで使う前提で計算します。")

    selected_item_ids: set[str] = set()
    grouped = group_items_by_category(items)

    tabs = st.tabs([CATEGORY_LABELS[category] for category in OPTIONAL_CATEGORIES])
    for tab, category in zip(tabs, OPTIONAL_CATEGORIES):
        with tab:
            category_items = grouped[category]
            if not category_items:
                st.info("このカテゴリのデータはありません。")
                continue

            cols = st.columns(2)
            for i, item in enumerate(category_items):
                with cols[i % 2]:
                    default_checked = True
                    checked = st.checkbox(
                        item_label(item, target_aspect),
                        value=default_checked,
                        key=f"owned_{item['id']}",
                        help=(
                            f"カテゴリ: {CATEGORY_LABELS.get(item['category'], item['category'])}\n\n"
                            f"要素: {aspects_text(item.get('aspects', {}))}\n\n"
                            f"消費: {'はい' if item.get('consumed', False) else 'いいえ'}\n\n"
                            f"メモ: {item.get('notes', '')}"
                        ),
                    )
                    if checked:
                        selected_item_ids.add(item["id"])

    available_items = [item for item in items if item["id"] in selected_item_ids]

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
                st.info(
                    f"組み合わせが多いため、過剰値が少ない順に{len(shown_results)}件だけ表示します。"
                )

            for i, result in enumerate(shown_results, start=1):
                render_result_card(result, target_aspect, int(target_value), i)
        else:
            shortage = int(target_value) - best["total"]
            st.error("目標値に届く組み合わせはありません。")
            st.metric("現在の最大値", best["total"])
            st.metric("不足値", shortage)

            st.markdown("**最大値になる組み合わせ**")
            render_item_table(best["items"], target_aspect)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**消費されるもの**")
                if best["consumed"]:
                    for item in best["consumed"]:
                        st.write(f"- {item_label(item, target_aspect)}")
                else:
                    st.write("- なし")
            with col2:
                st.markdown("**消費されないもの**")
                if best["not_consumed"]:
                    for item in best["not_consumed"]:
                        st.write(f"- {item_label(item, target_aspect)}")
                else:
                    st.write("- なし")

    with st.expander("データの増やし方"):
        st.markdown(
            f"""
データは次のJSONファイルで管理しています。

`{DATA_PATH}`

支援者を増やす場合は `assistants` 配列に、アイテムを増やす場合は `items` 配列に追加してください。

```json
{{
  "id": "leathy",
  "name_ja": "レアシー",
  "name_en": "Leathy",
  "category": "drink",
  "aspects": {{
    "grail": 2,
    "moth": 4,
    "nectar": 2,
    "scale": 2
  }},
  "consumed": true,
  "notes": "月10または蜜10＋飲み物で作れる"
}}
```

使えるカテゴリ:

- `assistant`
- `soul`
- `memory`
- `food`
- `drink`
- `tool`
- `special`

使える要素:

{", ".join(f"`{aspect}`" for aspect in ASPECTS)}
"""
        )


if __name__ == "__main__":
    main()
