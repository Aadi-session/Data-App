import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str) -> str:
    """Try st.secrets first (Streamlit Cloud), then env var (local .env)."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.environ.get(key, "")


OPENAI_API_KEY = _get_secret("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
MAX_TOKENS = 6000
TEMPERATURE = 0.7

# --- Groq configuration (uncomment to switch from OpenAI to Groq) ---
# GROQ_API_KEY = _get_secret("GROQ_API_KEY")
# GROQ_MODEL = "llama-3.3-70b-versatile"
# GROQ_MAX_TOKENS = 6000
# GROQ_TEMPERATURE = 0.7

DOMAIN_OPTIONS = [
    "Marketing",
    "Sales",
    "Finance",
    "Product",
    "Engineering",
    "Customer Success",
    "Supply Chain",
    "HR / People",
    "Operations",
    "Cross-functional",
    "Other",
]

CONSUMER_TYPE_OPTIONS = [
    "Data Analysts",
    "Data Scientists",
    "Business Users",
    "ML Models / Pipelines",
    "Downstream Applications",
    "External Partners",
    "BI Dashboards",
]

INGESTION_PATTERN_OPTIONS = [
    "Batch",
    "CDC",
    "Streaming",
    "API",
    "File Upload",
]

CRITICALITY_OPTIONS = ["High", "Medium", "Low"]

FRESHNESS_OPTIONS = [
    "Real-time (< 1 minute)",
    "Near real-time (1–15 minutes)",
    "Hourly",
    "Daily (standard batch)",
    "Weekly or less frequent",
]

CONSUMPTION_MODE_OPTIONS = [
    "SQL / Data Warehouse table",
    "BI Dashboard (Tableau, Looker, etc.)",
    "API endpoint",
    "File export (CSV, Parquet)",
    "ML Feature Store",
    "Event stream / Pub-Sub",
    "Reverse ETL to SaaS tools",
    "Notebook / ad-hoc analysis",
]

SENSITIVITY_OPTIONS = [
    "No sensitive data",
    "Yes — contains PII (names, emails, phone, addresses)",
    "Yes — contains financial data",
    "Yes — contains health / medical data",
    "Yes — multiple categories",
]

QUALITY_DIMENSION_OPTIONS = [
    "Completeness — no missing values in critical fields",
    "Uniqueness — no duplicate records",
    "Accuracy — values match source of truth",
    "Freshness — data arrives on time",
    "Validity — values conform to expected formats/ranges",
    "Consistency — same data matches across systems",
]

TIMELINE_OPTIONS = [
    "ASAP / This sprint",
    "This month",
    "This quarter",
    "Next quarter",
    "No specific deadline",
]

SAVED_PRDS_DIR = "saved_prds"
