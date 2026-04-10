import streamlit as st
from config import (
    CONSUMER_TYPE_OPTIONS,
    INGESTION_PATTERN_OPTIONS,
    CRITICALITY_OPTIONS,
)


def _ensure_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def tag_input(label: str, key: str, placeholder: str = "Type and press Enter"):
    """Renders a text input that accumulates values into a tag list."""
    _ensure_state(key, [])

    st.markdown(f"**{label}**")
    cols = st.columns([4, 1])
    input_val = cols[0].text_input(
        label, key=f"{key}_input", placeholder=placeholder, label_visibility="collapsed"
    )
    if cols[1].button("Add", key=f"{key}_add", use_container_width=True):
        val = input_val.strip()
        if val and val not in st.session_state[key]:
            st.session_state[key].append(val)
            st.rerun()

    if st.session_state[key]:
        pills_html = " ".join(
            f'<span style="background:rgba(84,222,209,0.15);color:#35505B;padding:4px 12px;'
            f'border-radius:16px;margin:2px 4px;display:inline-block;font-size:0.85rem;font-weight:500;">'
            f'{tag} &times;</span>'
            for tag in st.session_state[key]
        )
        st.markdown(pills_html, unsafe_allow_html=True)

        remove_tag = st.selectbox(
            "Remove a tag",
            options=[""] + st.session_state[key],
            key=f"{key}_remove",
            label_visibility="collapsed",
        )
        if remove_tag:
            st.session_state[key].remove(remove_tag)
            st.rerun()

    return list(st.session_state[key])


def data_source_input(key: str = "data_sources"):
    """Dynamic form for adding upstream data sources with name, pattern, and criticality."""
    _ensure_state(key, [])

    st.markdown("**Upstream Data Sources**")
    st.caption("Add each source system that feeds into this data product.")

    for i, source in enumerate(st.session_state[key]):
        with st.container():
            cols = st.columns([3, 2, 2, 1])
            new_name = cols[0].text_input(
                "Source", value=source["name"], key=f"{key}_name_{i}", label_visibility="collapsed"
            )
            new_pattern = cols[1].selectbox(
                "Pattern",
                INGESTION_PATTERN_OPTIONS,
                index=INGESTION_PATTERN_OPTIONS.index(source["pattern"]),
                key=f"{key}_pattern_{i}",
                label_visibility="collapsed",
            )
            new_crit = cols[2].selectbox(
                "Criticality",
                CRITICALITY_OPTIONS,
                index=CRITICALITY_OPTIONS.index(source["criticality"]),
                key=f"{key}_crit_{i}",
                label_visibility="collapsed",
            )
            if cols[3].button("✕", key=f"{key}_del_{i}", use_container_width=True):
                st.session_state[key].pop(i)
                st.rerun()

            st.session_state[key][i] = {
                "name": new_name,
                "pattern": new_pattern,
                "criticality": new_crit,
            }

    if not st.session_state[key]:
        cols = st.columns([3, 2, 2])
        cols[0].caption("Source name")
        cols[1].caption("Ingestion pattern")
        cols[2].caption("Criticality")

    if st.button("＋ Add source", key=f"{key}_add"):
        st.session_state[key].append(
            {"name": "", "pattern": "Batch", "criticality": "High"}
        )
        st.rerun()

    return list(st.session_state[key])


def consumer_input(key: str = "consumers"):
    """Multi-select consumer types with a per-consumer 'what do they need?' text input."""
    _ensure_state(f"{key}_types", [])
    _ensure_state(f"{key}_needs", {})

    selected = st.multiselect(
        "Who will consume this data product?",
        CONSUMER_TYPE_OPTIONS,
        default=st.session_state[f"{key}_types"],
        key=f"{key}_multiselect",
    )
    st.session_state[f"{key}_types"] = selected

    for consumer_type in selected:
        prev = st.session_state[f"{key}_needs"].get(consumer_type, "")
        need = st.text_input(
            f"What do **{consumer_type}** need from it?",
            value=prev,
            key=f"{key}_need_{consumer_type}",
            placeholder="e.g. Campaign performance metrics for weekly reporting",
        )
        st.session_state[f"{key}_needs"][consumer_type] = need

    result = []
    for ct in selected:
        result.append({"type": ct, "need": st.session_state[f"{key}_needs"].get(ct, "")})
    return result


def repeatable_text_input(
    label: str, key: str, placeholder: str = "", min_items: int = 1, max_items: int = 5
):
    """Text input that allows adding multiple entries (e.g. success metrics)."""
    _ensure_state(key, [""] * min_items)

    st.markdown(f"**{label}**")
    items = st.session_state[key]

    updated = []
    for i, item in enumerate(items):
        cols = st.columns([5, 1])
        val = cols[0].text_input(
            f"Item {i+1}",
            value=item,
            key=f"{key}_item_{i}",
            placeholder=placeholder,
            label_visibility="collapsed",
        )
        updated.append(val)
        if len(items) > min_items:
            if cols[1].button("✕", key=f"{key}_del_{i}"):
                st.session_state[key].pop(i)
                st.rerun()

    st.session_state[key] = updated

    if len(items) < max_items:
        if st.button("＋ Add another", key=f"{key}_add"):
            st.session_state[key].append("")
            st.rerun()

    return [v for v in st.session_state[key] if v.strip()]
