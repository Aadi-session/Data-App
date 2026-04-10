import streamlit as st
from pathlib import Path

from config import (
    DOMAIN_OPTIONS,
    FRESHNESS_OPTIONS,
    CONSUMPTION_MODE_OPTIONS,
    SENSITIVITY_OPTIONS,
    QUALITY_DIMENSION_OPTIONS,
    TIMELINE_OPTIONS,
)
from components import (
    tag_input,
    data_source_input,
    consumer_input,
    repeatable_text_input,
)
from generator import generate_prd_stream
from storage import save_prd, load_prd, list_saved_prds, delete_prd
from presets import PRESETS
from sample_prds import SAMPLE_PRDS
from export_utils import render_pdf_bytes

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Product PRD Generator — Modern",
    page_icon="https://www.themoderndatacompany.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "current_step": "stage1",
    "generated_markdown": "",
    "active_prd_id": None,
    "viewing_sample": None,
    "product_name": "",
    "domain": DOMAIN_OPTIONS[0],
    "problem_statement": "",
    "consumers_types": [],
    "consumers_needs": {},
    "data_sources": [],
    "entities": [],
    "metrics": [],
    "dimensions": [],
    "freshness": FRESHNESS_OPTIONS[3],
    "consumption_modes": [],
    "sensitivity": SENSITIVITY_OPTIONS[0],
    "compliance": "",
    "quality_dimensions": [],
    "success_metrics": [""],
    "timeline": TIMELINE_OPTIONS[4],
    "constraints": "",
}

for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _load_preset(name: str):
    """Populate session state from a preset dict."""
    preset = PRESETS[name]
    st.session_state.product_name = preset["product_name"]
    st.session_state.domain = preset["domain"]
    st.session_state.problem_statement = preset["problem_statement"]
    st.session_state.consumers_types = [c["type"] for c in preset["consumers"]]
    st.session_state.consumers_needs = {c["type"]: c["need"] for c in preset["consumers"]}
    st.session_state.data_sources = list(preset["data_sources"])
    st.session_state.entities = list(preset["entities"])
    st.session_state.metrics = list(preset["metrics"])
    st.session_state.dimensions = list(preset["dimensions"])
    st.session_state.freshness = preset["freshness"]
    st.session_state.consumption_modes = list(preset["consumption_modes"])
    st.session_state.sensitivity = preset["sensitivity"]
    st.session_state.compliance = preset.get("compliance", "")
    st.session_state.quality_dimensions = list(preset["quality_dimensions"])
    st.session_state.success_metrics = list(preset["success_metrics"])
    st.session_state.timeline = preset["timeline"]
    st.session_state.constraints = preset.get("constraints", "")
    st.session_state.current_step = "stage1"
    st.session_state.generated_markdown = ""
    st.session_state.active_prd_id = None
    st.session_state.viewing_sample = None


def _load_saved(prd_id: str):
    data = load_prd(prd_id)
    if data is None:
        st.error("PRD not found.")
        return
    inputs = data["inputs"]
    st.session_state.product_name = inputs.get("product_name", "")
    st.session_state.domain = inputs.get("domain", DOMAIN_OPTIONS[0])
    st.session_state.problem_statement = inputs.get("problem_statement", "")

    consumers = inputs.get("consumers", [])
    st.session_state.consumers_types = [c["type"] for c in consumers]
    st.session_state.consumers_needs = {c["type"]: c.get("need", "") for c in consumers}

    st.session_state.data_sources = inputs.get("data_sources", [])
    st.session_state.entities = inputs.get("entities", [])
    st.session_state.metrics = inputs.get("metrics", [])
    st.session_state.dimensions = inputs.get("dimensions", [])
    st.session_state.freshness = inputs.get("freshness", FRESHNESS_OPTIONS[3])
    st.session_state.consumption_modes = inputs.get("consumption_modes", [])
    st.session_state.sensitivity = inputs.get("sensitivity", SENSITIVITY_OPTIONS[0])
    st.session_state.compliance = inputs.get("compliance", "")
    st.session_state.quality_dimensions = inputs.get("quality_dimensions", [])
    st.session_state.success_metrics = inputs.get("success_metrics", [""])
    st.session_state.timeline = inputs.get("timeline", TIMELINE_OPTIONS[4])
    st.session_state.constraints = inputs.get("constraints", "")

    st.session_state.generated_markdown = data.get("markdown", "")
    st.session_state.active_prd_id = prd_id
    st.session_state.current_step = "preview" if data.get("markdown") else "stage1"
    st.session_state.viewing_sample = None


def _reset():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v if not isinstance(v, (list, dict)) else type(v)(v)


def _collect_inputs() -> dict:
    consumers = []
    for ct in st.session_state.get("consumers_types", []):
        consumers.append({
            "type": ct,
            "need": st.session_state.get("consumers_needs", {}).get(ct, ""),
        })
    return {
        "product_name": st.session_state.product_name,
        "domain": st.session_state.domain,
        "problem_statement": st.session_state.problem_statement,
        "consumers": consumers,
        "data_sources": st.session_state.data_sources,
        "entities": st.session_state.entities,
        "metrics": st.session_state.metrics,
        "dimensions": st.session_state.dimensions,
        "freshness": st.session_state.freshness,
        "consumption_modes": st.session_state.consumption_modes,
        "sensitivity": st.session_state.sensitivity,
        "compliance": st.session_state.compliance,
        "quality_dimensions": st.session_state.quality_dimensions,
        "success_metrics": [m for m in st.session_state.success_metrics if m.strip()],
        "timeline": st.session_state.timeline,
        "constraints": st.session_state.constraints,
    }


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # -- Brand logo --
    logo_path = Path(__file__).parent / "assets" / "modern-logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=160)

    st.caption("Data Product PRD Generator")

    st.divider()

    if st.button("✨ New PRD", use_container_width=True):
        _reset()
        st.rerun()

    # -- Sample PRDs (complete examples) --
    st.markdown("**Sample PRDs**")
    st.caption("View complete PRD examples before you start.")
    for sample_name, sample_data in SAMPLE_PRDS.items():
        if st.button(
            f"📄 {sample_name}",
            key=f"sample_{sample_name}",
            use_container_width=True,
            help=sample_data["description"],
        ):
            st.session_state.viewing_sample = sample_name
            st.session_state.current_step = "sample_view"
            st.rerun()

    st.divider()

    # -- Presets (pre-fill form fields) --
    st.markdown("**Quick-Start Templates**")
    st.caption("Pre-fill the form with sample inputs.")
    for name in PRESETS:
        if st.button(name, key=f"preset_{name}", use_container_width=True):
            _load_preset(name)
            st.rerun()

    st.divider()

    # -- Saved PRDs --
    saved = list_saved_prds()
    if saved:
        st.markdown("**Saved PRDs**")
        for item in saved[:10]:
            label = f"{item['name']}"
            col_load, col_del = st.columns([4, 1])
            if col_load.button(label, key=f"load_{item['id']}", use_container_width=True):
                _load_saved(item["id"])
                st.rerun()
            if col_del.button("🗑", key=f"del_{item['id']}"):
                delete_prd(item["id"])
                st.rerun()


# ---------------------------------------------------------------------------
# Stage renderers
# ---------------------------------------------------------------------------
def render_sample_view():
    """Display a complete sample PRD for reference."""
    sample_name = st.session_state.viewing_sample
    if sample_name not in SAMPLE_PRDS:
        st.warning("Sample not found.")
        st.session_state.current_step = "stage1"
        st.rerun()
        return

    sample = SAMPLE_PRDS[sample_name]

    st.markdown(
        f"""<div class="sample-prd-banner">
        <h3>📄 Sample PRD: {sample_name}</h3>
        <p>{sample["description"]}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to Generator", use_container_width=True):
            st.session_state.viewing_sample = None
            st.session_state.current_step = "stage1"
            st.rerun()
    with col2:
        matching_preset = None
        for preset_name in PRESETS:
            if sample["domain"] == PRESETS[preset_name]["domain"]:
                matching_preset = preset_name
                break
        if matching_preset:
            if st.button("🚀 Use Similar Template", use_container_width=True, type="primary"):
                _load_preset(matching_preset)
                st.rerun()
    with col3:
        safe_name = sample_name.lower().replace(" ", "-").replace("—", "").replace("  ", "-")
        st.download_button(
            "⬇ Download .md",
            data=sample["markdown"],
            file_name=f"sample-{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.divider()
    st.markdown(sample["markdown"], unsafe_allow_html=True)


def render_stage1():
    st.header("Stage 1 — The Problem & People")
    st.caption("Required — tell us what you're building and why.")

    st.session_state.product_name = st.text_input(
        "What is the name of your data product?",
        value=st.session_state.product_name,
        placeholder="e.g. Customer Insights, Revenue Metrics Hub",
        key="q1",
    )

    st.session_state.problem_statement = st.text_area(
        "What business problem does this solve?",
        value=st.session_state.problem_statement,
        placeholder=(
            "Describe the pain point. Who is affected? What breaks or is missing today?\n\n"
            "Example: Marketing has no unified view of campaign performance across channels. "
            "Analysts spend 4+ hours weekly pulling data from 3 tools and reconciling in spreadsheets."
        ),
        height=150,
        key="q2",
    )

    consumer_input(key="consumers")

    st.session_state.domain = st.selectbox(
        "Which domain or business unit does this belong to?",
        DOMAIN_OPTIONS,
        index=DOMAIN_OPTIONS.index(st.session_state.domain),
        key="q4",
    )

    st.divider()
    col1, col2 = st.columns(2)
    if col2.button("Next → Stage 2", use_container_width=True, type="primary"):
        if not st.session_state.product_name.strip():
            st.error("Please enter a product name.")
        elif not st.session_state.problem_statement.strip():
            st.error("Please describe the business problem.")
        else:
            st.session_state.current_step = "stage2"
            st.rerun()


def render_stage2():
    st.header("Stage 2 — The Data")
    st.caption("Required — describe the data that powers this product.")

    data_source_input(key="data_sources")

    st.divider()

    col_e, col_m, col_d = st.columns(3)
    with col_e:
        tag_input("Entities (IDs / keys)", "entities", "e.g. customer_id")
    with col_m:
        tag_input("Metrics / Measures", "metrics", "e.g. lifetime_value")
    with col_d:
        tag_input("Dimensions", "dimensions", "e.g. region, channel")

    st.divider()

    st.session_state.freshness = st.selectbox(
        "How fresh does the data need to be?",
        FRESHNESS_OPTIONS,
        index=FRESHNESS_OPTIONS.index(st.session_state.freshness),
        key="q7",
    )

    st.session_state.consumption_modes = st.multiselect(
        "How will this data product be consumed?",
        CONSUMPTION_MODE_OPTIONS,
        default=st.session_state.consumption_modes,
        key="q8",
    )

    st.divider()
    col1, col2, col3 = st.columns(3)
    if col1.button("← Back", use_container_width=True):
        st.session_state.current_step = "stage1"
        st.rerun()
    if col2.button("Skip to Generate", use_container_width=True):
        st.session_state.current_step = "generating"
        st.rerun()
    if col3.button("Next → Stage 3", use_container_width=True, type="primary"):
        st.session_state.current_step = "stage3"
        st.rerun()


def render_stage3():
    st.header("Stage 3 — Guardrails & Goals")
    st.caption("Optional but recommended — quality, governance, and timeline.")

    st.session_state.sensitivity = st.selectbox(
        "Does this data contain PII or sensitive information?",
        SENSITIVITY_OPTIONS,
        index=SENSITIVITY_OPTIONS.index(st.session_state.sensitivity),
        key="q9",
    )

    if st.session_state.sensitivity != SENSITIVITY_OPTIONS[0]:
        st.session_state.compliance = st.text_input(
            "Compliance requirements (GDPR, CCPA, HIPAA, SOC 2, etc.)",
            value=st.session_state.compliance,
            key="q9_compliance",
        )

    st.session_state.quality_dimensions = st.multiselect(
        "What data quality dimensions matter most?",
        QUALITY_DIMENSION_OPTIONS,
        default=st.session_state.quality_dimensions,
        key="q10",
    )

    st.divider()
    repeatable_text_input(
        "Measurable goals or success metrics",
        key="success_metrics",
        placeholder="e.g. Reduce weekly reporting time from 4 hours to < 10 minutes",
        min_items=1,
        max_items=5,
    )

    st.divider()

    st.session_state.timeline = st.selectbox(
        "Target timeline or launch date",
        TIMELINE_OPTIONS,
        index=TIMELINE_OPTIONS.index(st.session_state.timeline),
        key="q12",
    )

    st.session_state.constraints = st.text_area(
        "Any known constraints, dependencies, or risks?",
        value=st.session_state.constraints,
        placeholder="Tech limitations, team dependencies, data access issues...",
        height=100,
        key="q13",
    )

    st.divider()
    col1, _, col3 = st.columns(3)
    if col1.button("← Back", use_container_width=True):
        st.session_state.current_step = "stage2"
        st.rerun()
    if col3.button("🚀 Generate PRD", use_container_width=True, type="primary"):
        st.session_state.current_step = "generating"
        st.rerun()


def render_generating():
    st.header("Generating your PRD...")
    inputs = _collect_inputs()

    try:
        full_text = st.write_stream(generate_prd_stream(inputs))
        st.session_state.generated_markdown = full_text
        st.session_state.current_step = "preview"
        st.rerun()
    except Exception as e:
        st.error(f"Generation failed: {e}")
        if st.button("← Back to inputs"):
            st.session_state.current_step = "stage3"
            st.rerun()


def render_preview():
    md = st.session_state.generated_markdown
    if not md:
        st.warning("No PRD generated yet.")
        if st.button("← Back to inputs"):
            st.session_state.current_step = "stage1"
            st.rerun()
        return

    name = st.session_state.product_name or "data-product"
    safe_name = name.lower().replace(" ", "-")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("✏️ Edit Inputs", use_container_width=True):
            st.session_state.current_step = "stage1"
            st.rerun()
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.current_step = "generating"
            st.rerun()
    with col3:
        if st.button("💾 Save", use_container_width=True):
            inputs = _collect_inputs()
            prd_id = save_prd(inputs, md, st.session_state.active_prd_id)
            st.session_state.active_prd_id = prd_id
            st.toast("PRD saved!", icon="✅")
    with col4:
        st.download_button(
            "⬇ Download .md",
            data=md,
            file_name=f"{safe_name}-prd.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col5:
        pdf_bytes = render_pdf_bytes(md)
        if pdf_bytes:
            st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name=f"{safe_name}-prd.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("PDF unavailable", disabled=True, use_container_width=True)

    st.divider()
    st.markdown(md, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
step = st.session_state.current_step
if step == "sample_view":
    render_sample_view()
elif step == "stage1":
    render_stage1()
elif step == "stage2":
    render_stage2()
elif step == "stage3":
    render_stage3()
elif step == "generating":
    render_generating()
elif step == "preview":
    render_preview()
