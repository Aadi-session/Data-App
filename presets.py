PRESETS = {
    "Customer Insights": {
        "product_name": "Customer Insights",
        "domain": "Customer Success",
        "problem_statement": (
            "Customer data is scattered across CRM, billing, support tickets, and product "
            "analytics. Account managers have no single view of a customer's health, leading "
            "to missed churn signals and reactive engagement. Building a weekly customer "
            "health report takes 6+ hours of manual data wrangling."
        ),
        "consumers": [
            {"type": "Business Users", "need": "Unified customer health view for account reviews"},
            {"type": "Data Scientists", "need": "Feature-rich customer table for churn prediction model"},
            {"type": "BI Dashboards", "need": "Customer segmentation and retention dashboards"},
        ],
        "data_sources": [
            {"name": "Salesforce CRM", "pattern": "Batch", "criticality": "High"},
            {"name": "Stripe Billing", "pattern": "CDC", "criticality": "High"},
            {"name": "Zendesk Support", "pattern": "API", "criticality": "Medium"},
            {"name": "Product Analytics (Mixpanel)", "pattern": "Batch", "criticality": "Medium"},
        ],
        "entities": ["customer_id", "account_id", "subscription_id", "ticket_id"],
        "metrics": ["lifetime_value", "churn_probability", "nps_score", "support_ticket_count", "mrr"],
        "dimensions": ["segment", "plan_tier", "region", "signup_cohort", "industry"],
        "freshness": "Daily (standard batch)",
        "consumption_modes": [
            "SQL / Data Warehouse table",
            "BI Dashboard (Tableau, Looker, etc.)",
            "ML Feature Store",
        ],
        "sensitivity": "Yes — contains PII (names, emails, phone, addresses)",
        "compliance": "GDPR, SOC 2",
        "quality_dimensions": [
            "Completeness — no missing values in critical fields",
            "Uniqueness — no duplicate records",
            "Accuracy — values match source of truth",
        ],
        "success_metrics": [
            "Reduce customer health report generation from 6 hours to < 5 minutes",
            "Achieve 80% of account managers using the product within 60 days",
            "Improve churn prediction model AUC from 0.72 to 0.85",
        ],
        "timeline": "This quarter",
        "constraints": (
            "Salesforce API rate limits may slow initial backfill. "
            "Mixpanel data retention is only 90 days — need to set up ongoing export. "
            "PII handling must pass security review before launch."
        ),
    },
    "Revenue Metrics Hub": {
        "product_name": "Revenue Metrics Hub",
        "domain": "Finance",
        "problem_statement": (
            "Finance and RevOps teams spend the first 3 days of every month reconciling "
            "revenue numbers across Stripe, Salesforce, and the general ledger. Numbers "
            "rarely match on first pass, eroding trust in financial reporting. Board-level "
            "metrics like ARR, NRR, and expansion revenue are calculated in spreadsheets "
            "with conflicting definitions."
        ),
        "consumers": [
            {"type": "Data Analysts", "need": "Pre-computed revenue metrics for monthly reporting"},
            {"type": "Business Users", "need": "Self-serve ARR and NRR dashboards for leadership"},
            {"type": "Downstream Applications", "need": "Revenue data feed into FP&A planning tool"},
        ],
        "data_sources": [
            {"name": "Stripe Payments", "pattern": "CDC", "criticality": "High"},
            {"name": "Salesforce Opportunities", "pattern": "Batch", "criticality": "High"},
            {"name": "NetSuite General Ledger", "pattern": "Batch", "criticality": "High"},
        ],
        "entities": ["invoice_id", "subscription_id", "opportunity_id", "account_id"],
        "metrics": ["arr", "mrr", "nrr", "expansion_revenue", "churn_revenue", "gross_revenue"],
        "dimensions": ["month", "quarter", "product_line", "region", "sales_segment"],
        "freshness": "Daily (standard batch)",
        "consumption_modes": [
            "SQL / Data Warehouse table",
            "BI Dashboard (Tableau, Looker, etc.)",
            "Reverse ETL to SaaS tools",
        ],
        "sensitivity": "Yes — contains financial data",
        "compliance": "SOC 2, internal audit policy",
        "quality_dimensions": [
            "Accuracy — values match source of truth",
            "Completeness — no missing values in critical fields",
            "Consistency — same data matches across systems",
        ],
        "success_metrics": [
            "Month-end close revenue reconciliation in < 4 hours (down from 3 days)",
            "Single source of truth for ARR — zero conflicting definitions",
            "Finance team self-serves 80% of ad-hoc revenue queries",
        ],
        "timeline": "This month",
        "constraints": (
            "NetSuite exports are only available as nightly CSV drops. "
            "Revenue recognition rules differ by product line — need Finance sign-off. "
            "Must match auditor-approved GL numbers within ±0.01%."
        ),
    },
    "ML Feature Store": {
        "product_name": "ML Feature Store — User Behavior Features",
        "domain": "Engineering",
        "problem_statement": (
            "ML engineers rebuild the same user behavior features (session counts, "
            "clickstream aggregates, engagement scores) from scratch for every new model. "
            "Feature definitions drift across teams, causing training-serving skew. "
            "There is no centralized, versioned, low-latency feature serving layer."
        ),
        "consumers": [
            {"type": "Data Scientists", "need": "Discoverable, documented features for model training"},
            {"type": "ML Models / Pipelines", "need": "Low-latency feature vectors for online inference"},
            {"type": "Data Analysts", "need": "Feature usage and drift monitoring dashboards"},
        ],
        "data_sources": [
            {"name": "Kafka: user-clickstream", "pattern": "Streaming", "criticality": "High"},
            {"name": "PostgreSQL: users_db", "pattern": "CDC", "criticality": "High"},
            {"name": "Redis: session-store", "pattern": "API", "criticality": "Medium"},
        ],
        "entities": ["user_id", "session_id", "event_id"],
        "metrics": [
            "sessions_7d", "clicks_per_session", "engagement_score",
            "days_since_last_login", "conversion_rate_30d",
        ],
        "dimensions": ["platform", "device_type", "user_segment", "experiment_group"],
        "freshness": "Near real-time (1–15 minutes)",
        "consumption_modes": ["ML Feature Store", "API endpoint", "SQL / Data Warehouse table"],
        "sensitivity": "Yes — contains PII (names, emails, phone, addresses)",
        "compliance": "GDPR, CCPA",
        "quality_dimensions": [
            "Freshness — data arrives on time",
            "Completeness — no missing values in critical fields",
            "Consistency — same data matches across systems",
        ],
        "success_metrics": [
            "New model onboarding time from 2 weeks to < 2 days",
            "Zero training-serving skew across all production models",
            "Feature store serves 95th percentile requests in < 50ms",
        ],
        "timeline": "This quarter",
        "constraints": (
            "Kafka cluster is shared — need dedicated consumer group. "
            "Online serving latency budget is 50ms p95. "
            "Must support both batch (training) and real-time (serving) access patterns."
        ),
    },
    "Campaign Attribution": {
        "product_name": "Multi-Touch Campaign Attribution",
        "domain": "Marketing",
        "problem_statement": (
            "Marketing cannot accurately attribute conversions to campaigns across channels. "
            "Last-touch attribution in Google Analytics overstates paid search and ignores "
            "content marketing and email nurture sequences. The team has no way to measure "
            "true ROI per channel, leading to misallocated budget."
        ),
        "consumers": [
            {"type": "Data Analysts", "need": "Attribution-weighted conversion data for ROI analysis"},
            {"type": "Business Users", "need": "Channel performance dashboards with multi-touch view"},
            {"type": "Data Scientists", "need": "Touchpoint sequence data for attribution modeling"},
        ],
        "data_sources": [
            {"name": "Google Ads API", "pattern": "API", "criticality": "High"},
            {"name": "Facebook Ads API", "pattern": "API", "criticality": "High"},
            {"name": "HubSpot CRM", "pattern": "Batch", "criticality": "High"},
            {"name": "Snowplow Clickstream", "pattern": "Streaming", "criticality": "Medium"},
            {"name": "Stripe Conversions", "pattern": "CDC", "criticality": "High"},
        ],
        "entities": ["user_id", "touchpoint_id", "campaign_id", "conversion_id", "session_id"],
        "metrics": [
            "attributed_conversions", "attributed_revenue", "cost_per_acquisition",
            "roas", "touchpoints_per_conversion",
        ],
        "dimensions": ["channel", "campaign_name", "ad_group", "content_type", "conversion_window"],
        "freshness": "Daily (standard batch)",
        "consumption_modes": [
            "SQL / Data Warehouse table",
            "BI Dashboard (Tableau, Looker, etc.)",
            "Notebook / ad-hoc analysis",
        ],
        "sensitivity": "Yes — contains PII (names, emails, phone, addresses)",
        "compliance": "GDPR, CCPA",
        "quality_dimensions": [
            "Completeness — no missing values in critical fields",
            "Accuracy — values match source of truth",
            "Validity — values conform to expected formats/ranges",
        ],
        "success_metrics": [
            "Marketing team shifts from last-touch to multi-touch attribution for all reporting",
            "Identify at least 2 channels where budget reallocation improves ROAS by 15%+",
            "Reduce monthly attribution analysis from 5 days to same-day",
        ],
        "timeline": "Next quarter",
        "constraints": (
            "Ad platform APIs have rate limits and 24-48 hour data delays. "
            "Cross-device identity resolution is not solved — relying on logged-in user matching. "
            "Attribution window must be configurable (7, 14, 30 days)."
        ),
    },
}
