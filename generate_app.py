import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update calculate_combinations sort key
old_sort = """    results.sort(
        key=lambda r: (
            r["total"],
            len(r["items"]),
            len(r["consumed"]),
            ", ".join(item["id"] for item in r["items"]),
        )
    )"""

new_sort = """    results.sort(
        key=lambda r: (
            abs(r["total"] - target_value), # 目標値との差が少ない
            len(r["consumed"]),             # 消費アイテムが少ない
            sum(1 for i in r["items"] if i.get("rarity") == "rare"), # rareアイテムが少ない
            sum(1 for i in r["items"] if i.get("recipe")),           # クラフト品が少ない
            r["total"],                     # 合計値が高すぎない
        )
    )"""

code = code.replace(old_sort, new_sort)

# 2. In render_result_card, add item acquisition details expander
# Wait, let's inject it at the end of the function.
old_render_card = """        with col2:
            st.markdown("**消費されないもの**")
            if result["not_consumed"]:
                for item in result["not_consumed"]:
                    st.write(f"- {item_label(item, target_aspect)}")
            else:
                st.write("- なし")"""

new_render_card = old_render_card + """

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
                    details.append("**入手方法**:\\n" + "\\n".join(f"  - {h}" for h in item["how_to_get"]))
                if item.get("locations"):
                    details.append("**場所**:\\n" + "\\n".join(f"  - {l}" for l in item["locations"]))
                if item.get("recipe"):
                    rec = item["recipe"]
                    rec_str = ", ".join(f"{k}: {v}" for k, v in rec.items()) if isinstance(rec, dict) else str(rec)
                    details.append(f"**レシピ**: {rec_str}")
                    
                if details:
                    st.markdown("\\n\\n".join(details))
                else:
                    st.write("詳細データなし")
                st.divider()"""

code = code.replace(old_render_card, new_render_card)

with open("app_new.py", "w", encoding="utf-8") as f:
    f.write(code)

