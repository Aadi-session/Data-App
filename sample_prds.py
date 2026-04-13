SAMPLE_PRDS = {
    "Customer Insights": {
        "description": "A unified customer data product for account health scoring, churn prediction, and personalized engagement across CRM, billing, support, and product analytics.",
        "domain": "Customer Success",
        "markdown": """\
# Data Product PRD

> This document defines the requirements for the **Customer Insights — Unified Profile** data product.

---

| Item | Detail |
|---|---|
| **Product Name** | Customer Insights |
| **Owner** | Customer Data Team |
| **Domain** | Customer Success |
| **Status** | Draft |
| **Target Launch** | End of Q3 2026 |
| **Last Updated** | 2026-04-09 |

---

## 1. Problem & Context

### What problem does this solve?
Customer data is fragmented across Salesforce CRM, Stripe billing, Zendesk support tickets, and Mixpanel product analytics. Account managers have no unified view of a customer's health, usage trajectory, or risk profile. This leads to missed churn signals, reactive engagement, and inconsistent experiences across touchpoints. Building a weekly customer health report requires 6+ hours of manual data wrangling by analysts.

### How is this handled today?
Analysts manually pull exports from 4 systems every Monday, join them in Google Sheets, and distribute a static PDF report by Wednesday. Customer Success managers rely on gut feel and Salesforce notes to prioritize accounts. The ML team has attempted churn models twice, but abandoned both efforts due to inconsistent feature definitions and missing data.

### Why now?
Annual churn has increased from 8% to 14% over the past two quarters. Leadership has made customer retention a top company priority for H2 2026. The Customer Success team is scaling from 12 to 25 account managers and needs a self-serve health dashboard rather than a manual weekly report.

---

## 2. Goals & Success Metrics

### Goals
- Provide a single, trusted view of every customer across all touchpoints
- Enable proactive churn intervention by surfacing at-risk accounts automatically
- Reduce analyst time spent on manual customer reporting by 90%+
- Power the ML team's next-generation churn prediction model with consistent features
- Support customer segmentation for targeted campaigns

### Non-Goals
- Will not replace Salesforce as the system of record for sales activities
- Will not include real-time session-level clickstream data (product analytics will remain at daily aggregation level)
- Will not build the churn prediction model itself — this product provides the feature layer

### Success Metrics

| Metric | Baseline (Today) | Target | How Measured |
|---|---|---|---|
| Weekly customer health report generation time | 6+ hours manual | < 5 minutes automated | Pipeline run duration |
| Account manager adoption | 0% self-serve | 80% active users within 60 days | Dashboard access logs |
| Churn prediction model AUC | 0.72 (inconsistent features) | 0.85+ (unified features) | Model evaluation metrics |
| Data freshness | T+3 days (weekly manual) | T+1 day (daily automated) | Freshness monitor |
| Customer data completeness | ~60% (missing fields across systems) | > 95% on critical fields | Quality checks |

---

## 3. Users & Use Cases

### Target Consumers

| Consumer | Type | What They Need | How They'll Use It |
|---|---|---|---|
| Account Managers | Primary | Unified customer health scores, risk flags, and engagement history | Daily dashboard reviews, account prioritization |
| Customer Success Leadership | Primary | Segment-level health trends, churn cohort analysis | Weekly business reviews, board reporting |
| Data Scientists (ML Team) | Primary | Feature-rich, consistent customer table for model training | Direct table reads for churn and LTV models |
| Marketing Team | Secondary | Customer segments for targeted campaigns | Campaign audience building via reverse ETL |

### Key Use Cases

| Use Case | User | Trigger | Outcome |
|---|---|---|---|
| Daily account prioritization | Account Manager | Start of workday | Identify top 10 at-risk accounts to engage today |
| Monthly churn cohort analysis | CS Leadership | Month-end | Understand which segments are churning and why |
| Churn model retraining | Data Scientist | Monthly cycle | Updated model with fresh, consistent features |
| Win-back campaign targeting | Marketing | Quarterly | Identify recently churned accounts for re-engagement |

### Edge Cases to Handle
- Customers with multiple accounts across business units (entity resolution)
- Late-arriving Stripe webhook data causing temporary revenue calculation gaps
- Zendesk tickets linked to incorrect customer IDs
- Mixpanel anonymous user sessions not yet resolved to known customers
- Historical data gaps during Salesforce migration (2024)
- Customers who downgrade and re-upgrade within the same billing cycle

---

## 4. Data Product Definition

### Product Type
Dashboard-ready dataset + ML Feature Store table

### Core Outputs
- `customer_insights.dim_customers` — one row per customer, all attributes and latest health score
- `customer_insights.fct_customer_health_daily` — daily snapshot of health score and component metrics
- `customer_insights.fct_customer_events` — unified event timeline across all source systems
- `customer_insights.ml_features_customer` — wide, denormalized table optimized for ML consumption

### Consumption Interface
- **Account Managers & Leadership:** Tableau dashboards connected to the Snowflake tables
- **Data Scientists:** Direct Snowflake table access + Feature Store API
- **Marketing:** Reverse ETL (Census/Hightouch) syncing segments to HubSpot

### Key Entities & Metrics Exposed
- **Entities:** `customer_id`, `account_id`, `subscription_id`, `ticket_id`, `user_id`
- **Metrics:** `lifetime_value`, `mrr`, `churn_probability`, `health_score`, `nps_score`, `support_ticket_count_30d`, `product_usage_score`, `days_since_last_login`
- **Dimensions:** `segment`, `plan_tier`, `region`, `signup_cohort`, `industry`, `account_manager`

---

## 5. Data Sources & Lineage

### Source Systems

| Source | Owner | Data Domain | Ingestion Pattern | Criticality |
|---|---|---|---|---|
| Salesforce CRM | Sales Ops | Accounts, Contacts, Opportunities | Daily batch via Fivetran | High |
| Stripe Billing | Finance Eng | Subscriptions, Invoices, Payments | CDC via Fivetran | High |
| Zendesk Support | Support Ops | Tickets, Satisfaction Ratings | API poll every 6 hours | Medium |
| Mixpanel Analytics | Product Eng | User events, Sessions | Daily batch export | Medium |

### Key Source Entities
- **Salesforce:** `Account`, `Contact`, `Opportunity`, `Task`, `Note`
- **Stripe:** `Customer`, `Subscription`, `Invoice`, `Charge`, `Refund`
- **Zendesk:** `Ticket`, `User`, `Satisfaction_Rating`, `Comment`
- **Mixpanel:** `events` (session_start, feature_used, page_viewed), `user_profiles`

### Upstream Dependencies
- Fivetran Salesforce connector — if sync fails, account metadata goes stale (impact: health scores use outdated firmographic data)
- Stripe CDC — if delayed, MRR and LTV calculations will be off (impact: incorrect revenue-based health component)
- Mixpanel daily export — if delayed, product usage scores lag by an extra day (impact: moderate, usage trends smooth over daily gaps)

### Downstream Consumers
- Tableau Customer Health Dashboard — breaks if `dim_customers` schema changes or SLA is missed
- Churn prediction model pipeline — training fails if `ml_features_customer` is unavailable or has null spikes
- Census reverse ETL — marketing segments in HubSpot become stale if data is late

### Lineage
```
Salesforce (Fivetran) ──┐
Stripe (Fivetran CDC) ──┤
Zendesk (API) ──────────┤──→ Snowflake Raw ──→ dbt Staging ──→ dbt Intermediate ──→ dbt Marts
Mixpanel (Batch) ───────┘                      (cleaning,       (entity resolution,   (dim_customers,
                                                 dedup,           joins, business        fct_health_daily,
                                                 typing)          logic)                 ml_features)
```

---

## 6. Schema & Business Logic

### Grain
- `dim_customers`: One row per customer (SCD Type 2 for historical tracking)
- `fct_customer_health_daily`: One row per customer per day
- `ml_features_customer`: One row per customer (latest snapshot)

### Key Fields

| Field | Type | Description | Source | Business Rules |
|---|---|---|---|---|
| customer_id | STRING | Unified customer identifier | Entity resolution across sources | Deduplicated on Salesforce Account ID as primary key |
| health_score | FLOAT | Composite health score (0-100) | Calculated | Weighted: 40% usage + 30% support + 20% payment + 10% engagement |
| mrr | DECIMAL | Monthly recurring revenue | Stripe | Current active subscription amount, excludes one-time charges |
| lifetime_value | DECIMAL | Total revenue to date | Stripe | Sum of all successful charges minus refunds |
| churn_probability | FLOAT | ML-predicted churn risk (0-1) | ML model output | Updated monthly, NULL until first model run |
| nps_score | INTEGER | Latest NPS survey score | Salesforce | Most recent survey response, NULL if never surveyed |
| support_ticket_count_30d | INTEGER | Open + resolved tickets in last 30 days | Zendesk | Rolling 30-day window |
| product_usage_score | FLOAT | Composite product engagement (0-100) | Mixpanel | Based on DAU/MAU ratio, feature breadth, session depth |
| plan_tier | STRING | Current subscription plan | Stripe | Maps Stripe price IDs to business tier names |
| signup_date | DATE | First subscription start date | Stripe | Earliest `subscription.created` event |

### Business Logic & Transformations
- **Entity Resolution:** Customers are matched across systems using `email` as the primary join key, falling back to `company_name + domain` fuzzy matching for accounts without email overlap
- **Health Score Calculation:** Weighted composite of four components — usage score (40%), support sentiment (30%), payment health (20%), and engagement recency (10%). Each component normalized to 0-100 scale
- **MRR Calculation:** Sum of active subscription line items, prorated for mid-cycle changes, excluding one-time charges and credits
- **Deduplication:** Stripe customers with multiple payment profiles for the same company are merged using Salesforce Account ID as the canonical reference
- **SCD Type 2:** Customer dimension tracks changes to plan_tier, segment, and account_manager with valid_from/valid_to date ranges

### Data Modeling Approach
Star schema for the BI-facing layer (dim_customers, fct_customer_health_daily) to support fast, intuitive dashboard queries. A separate wide, denormalized table (ml_features_customer) for ML consumption — this avoids forcing data scientists to write complex joins and ensures training-serving consistency.

### Historical Backfill
- 24 months of historical data required for churn model training
- One-time backfill from Stripe (full history available), Salesforce (full history), Zendesk (12 months via API pagination), and Mixpanel (90 days only — historical export requested from vendor)
- Backfill estimated at 3-4 days of pipeline runtime for ~2M customer-day records

---

## 7. Data Quality & SLAs

### Quality Requirements

| Dimension | Rule | Threshold | Action on Breach |
|---|---|---|---|
| Completeness | `customer_id` must not be null | 100% | Block pipeline, alert owner |
| Completeness | `mrr` populated for all active subscribers | > 99.5% | Warn, investigate missing records |
| Uniqueness | No duplicate `customer_id` in dim_customers | 100% | Deduplicate and alert |
| Freshness | Data available by 06:00 UTC daily | 99.5% of runs | Alert on-call, page if > 2 hours late |
| Accuracy | MRR total matches Stripe dashboard within tolerance | ±0.5% | Trigger reconciliation review |
| Validity | `health_score` between 0 and 100 | 100% | Clamp and warn |

### Service Levels

| Attribute | Target | Notes |
|---|---|---|
| Refresh cadence | Daily | Full refresh at 04:00 UTC |
| Freshness SLA | Data available by 06:00 UTC | 2-hour processing window |
| Availability | 99.9% uptime | Snowflake tables accessible 24/7 |
| Incident response | P1: 30 min, P2: 4 hours | Paged via PagerDuty for P1 |

### Testing Strategy
- Schema tests (not-null, unique, accepted_values) on all critical fields via dbt tests
- Row count reconciliation between source and staging layers
- Business logic unit tests for health score calculation (edge cases: new customer, churned customer, customer with no support tickets)
- Statistical anomaly detection on daily health score distribution (alert on > 2 standard deviation shift)
- End-to-end data reconciliation: MRR sum vs. Stripe billing dashboard

---

## 8. Governance & Security

### Data Classification
- **Confidential:** PII fields (customer_name, email, phone, address)
- **Internal:** Financial metrics (MRR, LTV, revenue)
- **Internal:** Behavioral data (usage scores, session counts)

### PII & Sensitive Data Handling
- `customer_name`, `email`, `phone` — masked in the general-access layer; raw values only in a restricted PII schema accessible to authorized roles
- `address` — excluded from the data product entirely; not needed for health scoring
- All PII fields tagged in the data catalog with `pii: true` metadata

### Access Control
- **Role-Based Access (RBAC):**
  - `customer_insights_viewer` — read access to non-PII tables (Account Managers, Marketing)
  - `customer_insights_pii` — read access including PII fields (CS Leadership, Legal)
  - `customer_insights_ml` — read access to ML feature tables (Data Scientists)
  - `customer_insights_admin` — full access including write (Data Engineering)
- Column-level security via Snowflake dynamic data masking on PII columns

### Compliance Requirements
- GDPR: Right-to-erasure supported via `customer_id`-based deletion pipeline (triggers cascading soft-delete across all tables)
- SOC 2: All access logged and auditable; quarterly access reviews

### Retention & Deletion
- Active customer data retained indefinitely (subject to annual review)
- Churned customer data retained for 24 months post-churn, then anonymized
- GDPR deletion requests processed within 72 hours

### Ownership

| Role | Person / Team |
|---|---|
| Product Owner | [TBD — Customer Data Team Lead] |
| Technical Owner | [TBD — Data Engineering] |
| Data Steward | [TBD — Customer Success Ops] |

---

## 9. Scope & Constraints

### In Scope (v1)
- Unified customer dimension table with entity resolution across all 4 sources
- Daily health score calculation (composite of usage, support, payment, engagement)
- ML feature table for churn prediction
- Tableau dashboard with account-level health views
- Historical backfill for 24 months

### Out of Scope (v1)
- Real-time health score updates (requires streaming architecture — planned for v2)
- Predictive churn model training and serving (separate ML project consumes our feature table)
- Customer-facing health reports (internal use only for v1)

### Future Scope (v2+)
- Real-time health score updates via streaming pipeline
- Customer journey mapping and lifecycle stage tracking
- Integration with product-led growth (PLG) scoring
- Self-serve segment builder for Marketing

### Assumptions
- Salesforce Account ID is the canonical customer identifier across systems
- Mixpanel will provide extended data export beyond 90-day retention window
- Email is a reliable join key for cross-system entity resolution (>90% match rate)
- Existing Snowflake infrastructure has sufficient capacity

### Constraints
- Salesforce API rate limits: 15,000 calls/day — may slow initial backfill
- Mixpanel standard retention is 90 days — need enterprise plan or manual export for history
- PII handling must pass security review before production launch
- Must use existing Snowflake and Airflow infrastructure (no new platform purchases)

---

## 10. Risks & Open Questions

### Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Entity resolution accuracy below 90% | High — unreliable health scores | Medium | Build manual review queue for unmatched records; iterate on matching logic |
| Salesforce schema changes without notice | High — pipeline failures | Medium | Schema drift detection via Great Expectations; subscribe to admin changelog |
| PII leakage in derived fields | Critical — compliance violation | Low | Automated PII scanning; column-level masking; quarterly access audit |
| Mixpanel history limited to 90 days | Medium — incomplete usage features for older customers | High | Request extended export from vendor; supplement with Salesforce activity data |
| Pipeline SLA missed during quarter-end Snowflake load | Medium — late health scores | Medium | Dedicated warehouse for Customer Insights; buffer SLA by 1 hour during peak periods |

### Open Questions

| Question | Owner | Due Date | Status |
|---|---|---|---|
| Can we get extended Mixpanel data export (>90 days)? | Product Engineering | 2026-05-01 | Open |
| What is the approved entity resolution logic for multi-account customers? | Customer Success Ops | 2026-04-25 | Open |
| Should churned customers be included in the health score table or excluded? | CS Leadership | 2026-04-20 | Open |
| What Snowflake roles and masking policies exist for PII? | Security Team | 2026-04-30 | Open |

---

## 11. Milestones & Rollout

### Timeline

| Phase | Description | Target Date | Exit Criteria |
|---|---|---|---|
| Discovery | Requirements finalized, source access confirmed | Week 1-2 | This PRD approved, all source connections tested |
| Build | Pipeline development, dbt models, quality tests | Week 3-6 | All models passing in staging, backfill complete |
| Validate | UAT with 3 Account Managers + ML team | Week 7-8 | Consumer sign-off, health scores validated against manual report |
| Launch | Production deployment, monitoring live | Week 9 | SLA met for 5 consecutive days |
| Iterate | Feedback collection, v1.1 improvements | Week 10-12 | 80% adoption target met |

### Launch Criteria
- [ ] All dbt tests passing (schema + business logic)
- [ ] Data quality scores > 95% across all dimensions
- [ ] SLA met for 5+ consecutive days
- [ ] At least 3 Account Managers validated health scores match reality
- [ ] ML team confirmed feature table meets training requirements
- [ ] Monitoring and alerting configured (Slack + PagerDuty)
- [ ] Documentation published in data catalog
- [ ] PII access controls verified by Security

---

## Appendix

### Glossary
| Term | Definition |
|---|---|
| Health Score | Composite metric (0-100) reflecting overall customer health based on usage, support, payment, and engagement signals |
| MRR | Monthly Recurring Revenue — the normalized monthly revenue from active subscriptions |
| NRR | Net Revenue Retention — measures revenue retained from existing customers including expansion and contraction |
| Entity Resolution | The process of matching and merging customer records across different source systems into a single unified profile |
| SCD Type 2 | Slowly Changing Dimension Type 2 — tracks historical changes by creating new rows with valid_from/valid_to date ranges |

### Sample Output
| customer_id | customer_name | health_score | mrr | churn_probability | plan_tier | support_tickets_30d | product_usage_score | segment |
|---|---|---|---|---|---|---|---|---|
| CUST-001 | Acme Corp | 82 | $4,500 | 0.12 | Enterprise | 1 | 78 | Enterprise |
| CUST-002 | Beta Inc | 45 | $800 | 0.67 | Professional | 5 | 32 | Mid-Market |
| CUST-003 | Gamma LLC | 91 | $12,000 | 0.05 | Enterprise | 0 | 89 | Enterprise |

### References
- Customer Success OKRs — H2 2026 Planning Document
- Churn Prediction Model RFC — ML Team
- Salesforce Data Dictionary — Sales Ops Wiki
- Snowflake Access Control Policy — Security Team Confluence
""",
    },
    "Supply Chain Demand Forecasting": {
        "description": "A demand forecasting data product that unifies POS, inventory, logistics, and weather data to power automated replenishment and procurement planning.",
        "domain": "Supply Chain",
        "markdown": """\
# Data Product PRD

> This document defines the requirements for the **Supply Chain Demand Forecasting** data product.

---

| Item | Detail |
|---|---|
| **Product Name** | Supply Chain Demand Forecasting |
| **Owner** | Supply Chain Analytics Team |
| **Domain** | Supply Chain |
| **Status** | Draft |
| **Target Launch** | Q4 2026 |
| **Last Updated** | 2026-04-09 |

---

## 1. Problem & Context

### What problem does this solve?
The supply chain team relies on spreadsheet-based demand planning that uses trailing 4-week averages with manual seasonal adjustments. This approach leads to chronic stockouts on high-velocity SKUs (estimated $2.3M in lost revenue last quarter) while simultaneously carrying 40% excess inventory on slow-moving items. Procurement decisions are made 2 weeks late because the planning cycle depends on manually consolidated data from 5 systems.

### How is this handled today?
Every Monday, a demand planner manually pulls POS data from the retail system, inventory snapshots from the WMS, and incoming shipment data from the TMS. These are reconciled in Excel with manually maintained SKU master data. The planner applies seasonal factors from a separate spreadsheet, adjusts for known promotions (communicated via email from Marketing), and produces a weekly demand forecast. The process takes 3 full days and the resulting forecast has a MAPE (Mean Absolute Percentage Error) of 35%.

### Why now?
The company is expanding from 120 to 200 retail locations by Q1 2027. The current manual process will not scale — each new location adds roughly 4 hours of weekly planning work. Additionally, the CFO has mandated a 20% reduction in working capital tied up in inventory, which requires significantly more accurate demand signals.

---

## 2. Goals & Success Metrics

### Goals
- Replace manual demand forecasting with an automated, ML-powered pipeline
- Reduce forecast error (MAPE) from 35% to under 15%
- Enable daily demand signals instead of weekly batch planning
- Reduce excess inventory carrying costs by 20%+ while maintaining fill rates above 97%
- Provide procurement with actionable reorder recommendations, not just forecasts

### Non-Goals
- Will not replace the WMS or TMS systems — integrates with them as sources
- Will not handle supplier relationship management or PO generation (consumption by procurement team is manual in v1)
- Will not include price optimization or dynamic pricing recommendations

### Success Metrics

| Metric | Baseline (Today) | Target | How Measured |
|---|---|---|---|
| Forecast accuracy (MAPE) | 35% | < 15% | Actual vs. forecasted demand comparison |
| Stockout rate | 8.5% of SKU-locations per week | < 3% | POS null-scan rate + inventory monitoring |
| Excess inventory (days of supply) | 62 days average | < 45 days | Inventory-to-sales ratio |
| Planning cycle time | 3 days per weekly cycle | < 2 hours daily | Pipeline run + review time |
| Procurement lead time savings | Decisions 2 weeks delayed | Same-day recommendations | Time from data to recommendation |

---

## 3. Users & Use Cases

### Target Consumers

| Consumer | Type | What They Need | How They'll Use It |
|---|---|---|---|
| Demand Planners | Primary | SKU-location level demand forecasts with confidence intervals | Daily review dashboard, exception-based management |
| Procurement Managers | Primary | Reorder point alerts and recommended order quantities | Procurement planning, supplier negotiation |
| Supply Chain VP | Secondary | Aggregate forecast accuracy KPIs, inventory health metrics | Monthly S&OP meetings, board reporting |
| ML Engineers | Secondary | Feature-engineered data for model retraining | Scheduled model retraining pipeline |

### Key Use Cases

| Use Case | User | Trigger | Outcome |
|---|---|---|---|
| Daily demand forecast review | Demand Planner | 06:00 AM dashboard refresh | Identify SKUs with demand spikes or anomalies |
| Automated reorder alerts | Procurement Manager | Inventory drops below reorder point | Place replenishment order with recommended quantity |
| Promotional demand lift planning | Demand Planner | Marketing announces upcoming promotion | Adjust forecast with promotional uplift factors |
| Monthly forecast accuracy review | Supply Chain VP | Month-end | Assess model performance, identify improvement areas |

### Edge Cases to Handle
- New product launches with zero historical sales data (cold-start problem)
- Store openings and closures mid-forecast period
- Extreme weather events causing demand spikes or supply disruption
- Promotional cannibalization effects between related SKUs
- Holiday and seasonal demand patterns that differ year-over-year
- Supply-constrained periods where historical demand was artificially suppressed

---

## 4. Data Product Definition

### Product Type
ML-ready dataset + analytical tables + alert-driven data feeds

### Core Outputs
- `demand.fct_daily_forecast` — SKU-location-day level demand forecast with confidence intervals
- `demand.fct_actual_vs_forecast` — daily comparison of forecasted vs. actual demand
- `demand.dim_sku` — enriched SKU master with category, lifecycle, velocity classification
- `demand.fct_reorder_recommendations` — daily reorder signals with recommended quantities
- `demand.ml_features_demand` — feature-engineered table for model training

### Consumption Interface
- **Demand Planners:** Looker dashboard with drill-down by region, category, and SKU
- **Procurement Managers:** Slack alerts for reorder triggers + Looker detail view
- **Supply Chain VP:** Looker executive summary with accuracy KPIs
- **ML Engineers:** Direct BigQuery table access for model retraining

### Key Entities & Metrics Exposed
- **Entities:** `sku_id`, `location_id`, `supplier_id`, `promotion_id`
- **Metrics:** `forecasted_units`, `actual_units`, `forecast_error_pct`, `days_of_supply`, `reorder_quantity`, `safety_stock_units`, `confidence_interval_lower`, `confidence_interval_upper`
- **Dimensions:** `category`, `subcategory`, `region`, `location_type`, `velocity_tier`, `season`, `promotion_flag`

---

## 5. Data Sources & Lineage

### Source Systems

| Source | Owner | Data Domain | Ingestion Pattern | Criticality |
|---|---|---|---|---|
| Oracle Retail POS | Retail Ops | Transactions, Sales | Daily batch (nightly extract) | High |
| Manhattan WMS | Warehouse Ops | Inventory, Receipts, Shipments | CDC via Debezium | High |
| BluJay TMS | Logistics | Inbound shipments, Lead times | Daily batch (API) | Medium |
| SAP MDM | Master Data Mgmt | SKU master, Supplier master | Batch (weekly full refresh) | High |
| Weather API (OpenWeatherMap) | External | Daily forecasts by location | API (daily pull) | Low |
| Promotion Calendar | Marketing | Planned promotions | Manual upload (CSV) | Medium |

### Key Source Entities
- **Oracle POS:** `transactions`, `transaction_lines`, `stores`
- **Manhattan WMS:** `inventory_snapshot`, `receipt_orders`, `shipment_orders`
- **BluJay TMS:** `inbound_shipments`, `carrier_performance`
- **SAP MDM:** `material_master`, `vendor_master`, `bill_of_materials`
- **Weather API:** `daily_forecast` (temperature, precipitation, severe weather alerts)

### Upstream Dependencies
- Oracle POS nightly extract — if delayed past 02:00 AM, forecast pipeline starts with stale sales data (impact: forecast accuracy degrades)
- Manhattan WMS CDC — if Debezium connector fails, inventory position is unknown (impact: reorder recommendations are blocked)
- SAP MDM weekly refresh — if stale, new SKUs won't appear in forecasts (impact: new product launches missed)

### Downstream Consumers
- Looker demand planning dashboards — stale if forecast pipeline is late
- Procurement team Slack alerts — missed reorder windows if alerts don't fire
- Monthly S&OP report — inaccurate if data is incomplete

### Lineage
```
POS (Batch) ────────┐
WMS (CDC) ──────────┤
TMS (API) ──────────┤──→ BigQuery Raw ──→ dbt Staging ──→ dbt Intermediate ──→ dbt Marts ──→ Looker / Slack
SAP MDM (Batch) ────┤                     (cleaning,       (joins, feature        (forecasts,     Alerts
Weather API ────────┤                      dedup)           engineering)            reorder recs)
Promo Calendar ─────┘
```

---

## 6. Schema & Business Logic

### Grain
- `fct_daily_forecast`: One row per SKU per location per day
- `fct_reorder_recommendations`: One row per SKU per location (only when reorder triggered)

### Key Fields

| Field | Type | Description | Source | Business Rules |
|---|---|---|---|---|
| sku_id | STRING | Unique product identifier | SAP MDM | Maps to material_master.material_number |
| location_id | STRING | Store or warehouse identifier | Oracle POS / WMS | Standardized across POS and WMS systems |
| forecast_date | DATE | Date the forecast applies to | Calculated | Always future-dated (T+1 through T+30) |
| forecasted_units | INTEGER | Predicted demand in units | ML model output | Rounded to whole units, minimum 0 |
| confidence_lower | INTEGER | Lower bound (90% CI) | ML model output | Used for safety stock calculation |
| confidence_upper | INTEGER | Upper bound (90% CI) | ML model output | Used for maximum order quantity |
| actual_units | INTEGER | Actual units sold | POS | Populated retroactively when actuals arrive |
| days_of_supply | FLOAT | Current inventory / avg daily demand | Calculated | Uses 30-day rolling average demand |
| reorder_point | INTEGER | Inventory level that triggers reorder | Calculated | Safety stock + (lead_time_days × avg_daily_demand) |

### Business Logic & Transformations
- **Sales Aggregation:** POS transaction lines aggregated to SKU-location-day level; returns and voids excluded
- **Inventory Position:** Latest WMS snapshot + in-transit inventory from TMS = available-to-sell
- **Feature Engineering:** 90+ features including trailing demand (7d, 14d, 30d, 90d), YoY comparisons, day-of-week patterns, promotion flags, weather features, holiday indicators
- **Forecast Generation:** XGBoost ensemble model generates 30-day rolling forecast daily; separate models per velocity tier (high/medium/low)
- **Reorder Logic:** Reorder triggered when projected inventory (current - forecasted demand over lead time) drops below safety stock. Recommended quantity = (target days of supply × avg daily demand) - current inventory

### Data Modeling Approach
Star schema with date, SKU, and location dimensions. Fact tables are partitioned by date for efficient time-range queries. The ML feature table is a wide, denormalized structure (90+ columns) to support direct model consumption without joins.

### Historical Backfill
- 3 years of POS sales history required for seasonal pattern detection
- 1 year of inventory snapshots for safety stock calibration
- Weather data backfill for 2 years to correlate with demand patterns
- Estimated backfill: ~500M rows across all fact tables, 2-3 days processing time

---

## 7. Data Quality & SLAs

### Quality Requirements

| Dimension | Rule | Threshold | Action on Breach |
|---|---|---|---|
| Completeness | POS sales data for all active locations | 100% of active stores | Block forecast, alert — cannot forecast with missing sales |
| Freshness | POS data loaded by 02:00 AM daily | 99% of days | Delay forecast run; alert if not loaded by 03:00 AM |
| Accuracy | Forecast MAPE at SKU-location level | < 15% (30-day rolling) | Trigger model retraining review |
| Validity | `forecasted_units` >= 0 | 100% | Clamp negative values to 0, warn |
| Consistency | Inventory position matches WMS within tolerance | ±2% | Reconciliation alert |

### Service Levels

| Attribute | Target | Notes |
|---|---|---|
| Refresh cadence | Daily | Forecast run at 03:00 AM after POS load |
| Freshness SLA | Forecasts available by 06:00 AM | 3-hour processing window |
| Availability | 99.5% uptime | BigQuery + Looker stack |
| Incident response | P1: 1 hour, P2: 8 hours | Paged via PagerDuty for P1 |

### Testing Strategy
- Schema tests (not-null, unique, accepted_values) on all dimension tables
- Forecast range tests (no negative values, reasonable upper bounds per SKU)
- Daily volume tests (row counts within 2 standard deviations of trailing 30-day average)
- Backtesting framework: compare model predictions against held-out historical data weekly
- Cross-source reconciliation: POS sales totals vs. Finance revenue reports

---

## 8. Governance & Security

### Data Classification
- **Internal:** All demand forecasting data (sales, inventory, forecasts)
- **Confidential:** Supplier pricing and lead time data from SAP

### PII & Sensitive Data Handling
- No customer PII in this data product (POS data is aggregated to SKU-location level, no customer identifiers)
- Supplier contract terms and pricing are classified as Confidential — access restricted to Procurement and Supply Chain leadership roles

### Access Control
- `demand_viewer` — read access to forecast and accuracy tables (Demand Planners, Operations)
- `demand_procurement` — read access including supplier data and reorder recommendations (Procurement Managers)
- `demand_admin` — full access including ML features and raw data (Data Engineering, ML Engineers)

### Compliance Requirements
- SOC 2: Access logging and annual audit
- Internal data governance policy: all tables registered in data catalog with ownership and freshness metadata

### Retention & Deletion
- Forecast data retained for 3 years (needed for model backtesting and seasonal analysis)
- Raw POS data retained for 5 years (aligns with finance retention policy)
- Aged data moved to cold storage after 18 months

### Ownership

| Role | Person / Team |
|---|---|
| Product Owner | [TBD — Supply Chain Analytics Lead] |
| Technical Owner | [TBD — Data Engineering] |
| Data Steward | [TBD — Demand Planning Manager] |

---

## 9. Scope & Constraints

### In Scope (v1)
- Daily SKU-location demand forecast (30-day horizon)
- Automated reorder point and quantity recommendations
- Forecast accuracy tracking and reporting
- Looker dashboards for demand planners and procurement
- Historical backfill for 3 years of sales data

### Out of Scope (v1)
- Price elasticity modeling (requires controlled pricing experiments — planned for v2)
- Automated PO generation (procurement will review recommendations manually in v1)
- Cannibalization modeling between related SKUs (complex cross-SKU dependencies)

### Future Scope (v2+)
- Price elasticity and promotion impact modeling
- Automated PO generation integrated with SAP procurement module
- Cross-SKU cannibalization and halo effect modeling
- Real-time demand sensing from e-commerce clickstream data

### Assumptions
- Oracle POS nightly extract will be available by 02:00 AM consistently
- SKU master data in SAP is reasonably accurate and up-to-date
- Weather has a measurable impact on demand for at least some product categories
- 3 years of historical POS data is sufficient for seasonal pattern detection

### Constraints
- Must use existing GCP/BigQuery infrastructure
- Oracle POS extract is batch-only — no real-time sales feed available
- WMS CDC via Debezium has a 5-minute lag — acceptable for daily forecasting, not for real-time
- Promotion calendar is manually maintained — data quality depends on Marketing discipline

---

## 10. Risks & Open Questions

### Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Cold-start problem for new SKUs | Medium — no history for ML model | High (50+ new SKUs/quarter) | Category-level fallback model for SKUs with < 90 days history |
| Oracle POS extract delays | High — cascading delay to all downstream | Medium | 1-hour buffer in SLA; automated alerting at 02:30 AM |
| Model accuracy degrades after promotional period | Medium — forecasts overshoot post-promotion | Medium | Separate promotion-aware model; post-promotion dampening logic |
| Weather API provider changes or goes down | Low — weather is supplementary feature | Low | Cache 7-day forecast; model degrades gracefully without weather features |
| Store expansion outpaces model retraining | Medium — poor forecasts for new locations | Medium | New location inherits forecast from most similar existing location until 90 days of data |

### Open Questions

| Question | Owner | Due Date | Status |
|---|---|---|---|
| Can we get real-time POS feed instead of nightly batch? | IT / Oracle Admin | 2026-06-15 | Open |
| Which product categories show strongest weather correlation? | Data Science | 2026-05-01 | In Progress |
| What is the approved safety stock formula and target service level? | Supply Chain VP | 2026-05-15 | Open |
| How will the promotion calendar be maintained going forward? | Marketing Ops | 2026-05-01 | Open |

---

## 11. Milestones & Rollout

### Timeline

| Phase | Description | Target Date | Exit Criteria |
|---|---|---|---|
| Discovery | Requirements finalized, source access confirmed, model approach selected | Week 1-3 | PRD approved, data access confirmed, baseline MAPE measured |
| Build — Data | Pipeline development, dbt models, feature engineering | Week 4-8 | All staging and intermediate models passing tests |
| Build — ML | Model training, hyperparameter tuning, backtesting | Week 8-11 | MAPE < 15% on backtesting holdout |
| Validate | UAT with 2 demand planners + procurement lead | Week 12-13 | Users confirm forecasts are actionable, reorder recs make sense |
| Launch | Production deployment, monitoring live | Week 14 | SLA met for 5 consecutive days, no P1 incidents |
| Iterate | Feedback, model tuning, dashboard refinements | Week 15-18 | Adoption by all 8 demand planners, procurement using reorder alerts |

### Launch Criteria
- [ ] Forecast MAPE < 15% on 30-day rolling basis
- [ ] All dbt tests passing (schema + business logic + reconciliation)
- [ ] Pipeline SLA met for 5+ consecutive days
- [ ] At least 2 demand planners validated forecasts against their domain knowledge
- [ ] Reorder recommendations reviewed and approved by procurement lead
- [ ] Monitoring and alerting configured (Slack + PagerDuty)
- [ ] All tables documented in data catalog

---

## Appendix

### Glossary
| Term | Definition |
|---|---|
| MAPE | Mean Absolute Percentage Error — standard metric for forecast accuracy, calculated as average of |actual - forecast| / actual |
| Safety Stock | Buffer inventory held to protect against demand variability and supply uncertainty |
| Reorder Point | Inventory level at which a replenishment order should be triggered |
| Days of Supply | Current inventory divided by average daily demand — indicates how many days inventory will last |
| Velocity Tier | SKU classification based on sales volume (High: top 20%, Medium: 20-60%, Low: bottom 40%) |
| Cold Start | The challenge of forecasting demand for new products with no sales history |

### Sample Output
| sku_id | location_id | forecast_date | forecasted_units | confidence_lower | confidence_upper | actual_units | days_of_supply |
|---|---|---|---|---|---|---|---|
| SKU-1042 | LOC-015 | 2026-04-10 | 84 | 71 | 97 | — | 12.3 |
| SKU-2201 | LOC-015 | 2026-04-10 | 312 | 280 | 344 | — | 5.1 |
| SKU-1042 | LOC-032 | 2026-04-10 | 45 | 38 | 52 | — | 22.7 |

### References
- Supply Chain S&OP Process Documentation — Operations Wiki
- Demand Planning Best Practices — Gartner Research (2025)
- Oracle POS Data Dictionary — IT Systems Documentation
- Inventory Optimization Policy — CFO-approved FY2026
""",
    },
    "Marketing Revenue Attribution": {
        "description": "A multi-touch attribution data product that connects ad platform, CRM, and conversion data to measure true channel ROI and optimize marketing spend.",
        "domain": "Marketing",
        "markdown": """\
# Data Product PRD

> This document defines the requirements for the **Marketing Revenue Attribution** data product.

---

| Item | Detail |
|---|---|
| **Product Name** | Marketing Revenue Attribution |
| **Owner** | Marketing Analytics Team |
| **Domain** | Marketing |
| **Status** | Draft |
| **Target Launch** | End of Q2 2026 |
| **Last Updated** | 2026-04-09 |

---

## 1. Problem & Context

### What problem does this solve?
Marketing spends $4.2M per quarter across 6 channels (paid search, paid social, content, email, events, and partnerships) but cannot accurately attribute revenue to campaigns. Last-touch attribution in Google Analytics overstates paid search by an estimated 40% and completely ignores the impact of content marketing and email nurture sequences. Budget allocation decisions are based on misleading data, resulting in an estimated 20-30% inefficiency in marketing spend.

### How is this handled today?
Each channel team reports their own "attributed revenue" using different methodologies and tools — Google Ads reports on paid search, HubSpot reports on email, and Salesforce reports on pipeline. These numbers are inconsistent and collectively exceed total company revenue by 2-3x due to double-counting. The Marketing Ops analyst spends 5 days each month attempting to reconcile these numbers in a spreadsheet, producing a "best guess" allocation that no one fully trusts.

### Why now?
The board has mandated a 15% improvement in marketing efficiency (revenue per marketing dollar) for FY2027 planning. The CMO cannot make defensible budget allocation decisions without accurate attribution. Additionally, the company is piloting a $500K ABM (Account-Based Marketing) program and needs to measure its incremental impact rigorously.

---

## 2. Goals & Success Metrics

### Goals
- Establish a single source of truth for marketing attribution across all channels
- Enable multi-touch attribution modeling (moving beyond last-touch)
- Reduce monthly attribution analysis from 5 days to same-day automated reporting
- Provide channel-level and campaign-level ROI metrics to support budget allocation
- Support A/B testing of attribution models (last-touch, linear, time-decay, data-driven)

### Non-Goals
- Will not build or manage the marketing automation platform (HubSpot remains the system of record for campaigns)
- Will not perform real-time bid optimization for paid channels (that remains in-platform)
- Will not replace Google Analytics for web analytics — this product focuses on revenue attribution, not traffic analytics

### Success Metrics

| Metric | Baseline (Today) | Target | How Measured |
|---|---|---|---|
| Monthly attribution analysis time | 5 days manual | Same-day (< 2 hours review) | Calendar tracking |
| Attribution model coverage | Last-touch only | 4 models available (last-touch, linear, time-decay, data-driven) | Model registry |
| Channel ROI visibility | Inconsistent, double-counted | Single consistent view, < 5% variance from total revenue | Attribution sum vs. actual revenue reconciliation |
| Budget reallocation impact | No data-driven reallocation | Identify 2+ channels where reallocation improves ROAS by 15% | Quarterly ROAS comparison |
| Data freshness | Monthly manual | Daily automated | Pipeline freshness monitor |

---

## 3. Users & Use Cases

### Target Consumers

| Consumer | Type | What They Need | How They'll Use It |
|---|---|---|---|
| Marketing Ops Analyst | Primary | Campaign-level and channel-level attribution data for reporting | Daily dashboard monitoring, monthly executive reporting |
| Channel Managers (Paid, Content, Email) | Primary | Their channel's attributed revenue and ROI with multi-touch view | Campaign optimization, budget justification |
| CMO / VP Marketing | Primary | Executive-level channel mix analysis with ROI benchmarks | Quarterly budget allocation, board reporting |
| Data Scientists | Secondary | Raw touchpoint-level data for custom attribution modeling | Advanced attribution model development |

### Key Use Cases

| Use Case | User | Trigger | Outcome |
|---|---|---|---|
| Daily campaign performance review | Marketing Ops | Start of day | Identify underperforming campaigns for optimization or pause |
| Monthly channel mix analysis | CMO | Month-end | Data-driven budget reallocation recommendations |
| Attribution model comparison | Data Scientist | Quarterly | Evaluate which attribution model best reflects reality |
| ABM program ROI measurement | VP Marketing | Campaign milestone | Justify continued investment or pivot strategy |

### Edge Cases to Handle
- Cross-device user journeys (desktop research → mobile conversion)
- Touchpoints with 30+ day gaps in the buyer journey
- Conversions with zero trackable marketing touchpoints (organic/direct)
- Ad blocker impact on impression and click tracking
- UTM parameter inconsistencies across teams
- Multi-stakeholder B2B deals with touchpoints across different contacts at the same account

---

## 4. Data Product Definition

### Product Type
Dashboard-ready analytical dataset + ML-ready touchpoint data

### Core Outputs
- `attribution.fct_touchpoints` — every marketing touchpoint in the buyer journey, timestamped and categorized
- `attribution.fct_conversions` — every conversion event with revenue, linked to account/contact
- `attribution.fct_attributed_revenue` — attributed revenue by touchpoint, under each attribution model
- `attribution.dim_campaigns` — unified campaign taxonomy across all channels
- `attribution.rpt_channel_roi` — pre-aggregated channel-level ROI metrics for dashboard performance

### Consumption Interface
- **Marketing Ops & Channel Managers:** Looker dashboards with model toggle (switch between attribution models)
- **CMO:** Looker executive dashboard with channel mix visualization
- **Data Scientists:** Direct Snowflake access to touchpoint-level data for custom modeling

### Key Entities & Metrics Exposed
- **Entities:** `account_id`, `contact_id`, `touchpoint_id`, `campaign_id`, `conversion_id`, `opportunity_id`
- **Metrics:** `attributed_revenue`, `cost`, `roas`, `cost_per_acquisition`, `touchpoints_per_conversion`, `avg_days_to_conversion`, `conversion_rate`
- **Dimensions:** `channel`, `campaign_name`, `content_type`, `ad_group`, `conversion_window`, `attribution_model`, `deal_stage`

---

## 5. Data Sources & Lineage

### Source Systems

| Source | Owner | Data Domain | Ingestion Pattern | Criticality |
|---|---|---|---|---|
| Google Ads API | Paid Search Team | Impressions, Clicks, Cost | Daily batch (API) | High |
| Facebook/Meta Ads API | Paid Social Team | Impressions, Clicks, Cost | Daily batch (API) | High |
| LinkedIn Ads API | ABM Team | Impressions, Clicks, Cost | Daily batch (API) | Medium |
| HubSpot CRM | Marketing Ops | Contacts, Email events, Forms | CDC via Fivetran | High |
| Salesforce CRM | Sales Ops | Opportunities, Accounts, Revenue | Daily batch via Fivetran | High |
| Snowplow Clickstream | Web Engineering | Page views, UTM parameters, Sessions | Real-time → daily aggregate | High |
| Stripe | Finance Eng | Payments, Revenue | CDC via Fivetran | High |

### Key Source Entities
- **Google/Meta/LinkedIn Ads:** `campaigns`, `ad_groups`, `ads`, `click_reports`, `cost_reports`
- **HubSpot:** `contacts`, `email_events` (sent, opened, clicked), `form_submissions`, `campaigns`
- **Salesforce:** `Opportunity`, `OpportunityContactRole`, `Account`, `CampaignMember`
- **Snowplow:** `page_views`, `sessions`, `structured_events` (with UTM parameters)
- **Stripe:** `charges`, `invoices`, `customers`

### Upstream Dependencies
- Google/Meta/LinkedIn Ads APIs — 24-48 hour data delay is inherent; if API access is revoked, paid channel data is unavailable
- HubSpot CDC — if Fivetran sync fails, email and form touchpoints are stale
- Salesforce daily sync — if delayed, revenue data for closed-won opportunities is missing (impact: attributed revenue is understated)
- Snowplow collector — if down, web touchpoints are lost permanently (no replay capability)

### Downstream Consumers
- Looker attribution dashboards — stale or broken if pipeline misses SLA
- Monthly board reporting deck — executive decisions depend on accurate channel ROI
- FY2027 budget planning model — uses attributed revenue as primary input

### Lineage
```
Ad Platforms (API) ──────┐
HubSpot (CDC) ───────────┤
Salesforce (Batch) ──────┤──→ Snowflake Raw ──→ dbt Staging ──→ dbt Intermediate ──→ dbt Marts ──→ Looker
Snowplow (Streaming) ────┤                      (cleaning,       (identity stitching,  (fct_attributed_
Stripe (CDC) ────────────┘                       UTM parsing,     touchpoint assembly,   revenue per model,
                                                  dedup)           attribution models)    rpt_channel_roi)
```

---

## 6. Schema & Business Logic

### Grain
- `fct_touchpoints`: One row per marketing touchpoint per contact
- `fct_attributed_revenue`: One row per touchpoint per attribution model per conversion

### Key Fields

| Field | Type | Description | Source | Business Rules |
|---|---|---|---|---|
| touchpoint_id | STRING | Unique touchpoint identifier | Generated (hash of contact + channel + timestamp) | Deduplicated on 1-hour session window |
| contact_id | STRING | Unified contact identifier | Identity stitching | Resolved across HubSpot, Salesforce, Snowplow via email match |
| account_id | STRING | B2B account identifier | Salesforce | Used for account-level attribution roll-up |
| channel | STRING | Marketing channel | Derived from UTM/source | Standardized taxonomy: paid_search, paid_social, email, content, organic, direct, events, partnerships |
| touchpoint_timestamp | TIMESTAMP | When the touchpoint occurred | Source system | UTC normalized |
| attributed_revenue | DECIMAL | Revenue attributed to this touchpoint | Calculated | Varies by attribution model; sum across all touchpoints = total revenue (within model) |
| attribution_model | STRING | Which model assigned the credit | Calculated | One of: last_touch, linear, time_decay, data_driven |
| conversion_id | STRING | The conversion event this touchpoint contributed to | Salesforce Opportunity | Linked via contact → opportunity contact role |
| campaign_id | STRING | Unified campaign identifier | Mapped from source campaign IDs | Cross-platform campaign mapping table maintained by Marketing Ops |

### Business Logic & Transformations
- **Identity Stitching:** Contacts matched across systems using email as primary key, with fallback to HubSpot contact ID → Salesforce contact mapping via Fivetran
- **Touchpoint Assembly:** All marketing interactions (ad clicks, email opens/clicks, content page views, form submissions, event registrations) unified into a single touchpoint timeline per contact
- **UTM Standardization:** UTM parameters parsed and mapped to a canonical channel/campaign taxonomy (handled via a mapping table to account for inconsistent tagging across teams)
- **Attribution Models:**
  - **Last-Touch:** 100% credit to the last touchpoint before conversion
  - **Linear:** Equal credit split across all touchpoints in the journey
  - **Time-Decay:** Exponentially more credit to touchpoints closer to conversion (7-day half-life)
  - **Data-Driven:** ML model (Shapley value-based) trained on historical conversion data
- **Conversion Matching:** A conversion is a Salesforce Opportunity reaching "Closed Won" stage. Revenue is the Opportunity amount, cross-validated with Stripe payment data
- **Attribution Window:** Configurable, defaulting to 90 days. Touchpoints older than the window are excluded from attribution

### Data Modeling Approach
Star schema centered on the touchpoint fact table, with dimension tables for campaigns, channels, contacts, and accounts. The attributed revenue fact table is a bridge table that stores credit allocation under each model. This approach supports dashboard toggle between models without recalculation at query time.

### Historical Backfill
- 12 months of historical touchpoint and conversion data for model training and trend analysis
- Ad platform API history varies: Google (full), Meta (2 years), LinkedIn (1 year)
- Snowplow data available for 6 months — older web touchpoints will not be available
- Estimated backfill: ~15M touchpoint records, ~50K conversions, 1-2 days processing

---

## 7. Data Quality & SLAs

### Quality Requirements

| Dimension | Rule | Threshold | Action on Breach |
|---|---|---|---|
| Completeness | All Closed Won opportunities have at least 1 touchpoint | > 90% | Investigate unattributed conversions, check identity stitching |
| Completeness | UTM parameters present on paid channel touchpoints | > 95% | Flag to channel managers for tagging compliance |
| Accuracy | Attributed revenue sum matches actual revenue (per model) | ±2% | Reconciliation review, check for missing conversions |
| Freshness | Data available by 09:00 AM daily | 99% of days | Alert Marketing Ops, delay dashboard review |
| Uniqueness | No duplicate touchpoints within 1-hour session window | 100% | Dedup and warn |
| Validity | `channel` value in canonical taxonomy | 100% | Map to "unknown" and flag for review |

### Service Levels

| Attribute | Target | Notes |
|---|---|---|
| Refresh cadence | Daily | Pipeline runs at 06:00 AM after all source syncs |
| Freshness SLA | Data available by 09:00 AM | 3-hour processing window |
| Availability | 99.5% | Snowflake + Looker |
| Incident response | P1: 1 hour, P2: 8 hours | Slack alert for P2, PagerDuty for P1 |

### Testing Strategy
- Schema tests on all dimension and fact tables (not-null, unique, accepted_values, relationships)
- Revenue reconciliation: sum of attributed_revenue under each model vs. total actual revenue (should match within ±2%)
- Touchpoint coverage: percentage of conversions with at least 1 attributed touchpoint (target > 90%)
- Model consistency: each model's total attributed revenue should equal total actual revenue
- UTM compliance: weekly report on percentage of paid clicks with valid UTM parameters

---

## 8. Governance & Security

### Data Classification
- **Confidential:** Contact PII (name, email) in touchpoint data
- **Internal:** Campaign performance and spend data
- **Internal:** Revenue attribution data

### PII & Sensitive Data Handling
- Contact `email` and `name` used for identity stitching but masked in the dashboard-facing layer
- Only `contact_id` (hashed) exposed in Looker-accessible tables
- Raw PII available only in restricted staging tables for identity stitching pipeline

### Access Control
- `attribution_viewer` — read access to aggregated dashboard tables (Channel Managers, Marketing Ops)
- `attribution_analyst` — read access including touchpoint-level data, no PII (Marketing Ops Analyst)
- `attribution_pii` — read access to PII tables for identity stitching debugging (Data Engineering)
- `attribution_admin` — full access (Data Engineering, Marketing Analytics Lead)

### Compliance Requirements
- GDPR: Touchpoint data tied to EU contacts must respect consent flags from HubSpot; opt-out contacts excluded from attribution
- CCPA: California contacts can request data deletion — cascading delete through touchpoint tables
- Ad platform TOS: No raw click-level data exported to third parties

### Retention & Deletion
- Attribution data retained for 24 months for trend analysis
- Touchpoint-level raw data archived to cold storage after 12 months
- GDPR/CCPA deletion requests processed within 72 hours via contact_id cascade

### Ownership

| Role | Person / Team |
|---|---|
| Product Owner | [TBD — Marketing Analytics Lead] |
| Technical Owner | [TBD — Data Engineering] |
| Data Steward | [TBD — Marketing Ops] |

---

## 9. Scope & Constraints

### In Scope (v1)
- Unified touchpoint timeline across all 6 channels
- Identity stitching across HubSpot, Salesforce, and Snowplow
- Four attribution models (last-touch, linear, time-decay, data-driven)
- Looker dashboards with model toggle for channel-level and campaign-level ROI
- 12-month historical backfill

### Out of Scope (v1)
- View-through attribution for display/video ads (requires impression-level data integration — planned for v2)
- Offline event attribution (conferences, field events) beyond what's tracked in Salesforce campaigns
- Incrementality testing (requires controlled holdout experiments — planned for v2)

### Future Scope (v2+)
- View-through attribution for display and video campaigns
- Incrementality/lift testing framework with controlled holdout groups
- Self-serve attribution model builder for Marketing Data Scientists
- Integration with media mix modeling (MMM) for top-of-funnel channel optimization

### Assumptions
- Email is a reliable identity key across HubSpot, Salesforce, and Snowplow (>85% match rate expected)
- UTM parameters are present on >90% of paid channel clicks (current compliance unknown — to be measured)
- Salesforce Opportunity amount is the canonical revenue figure for attribution
- 90-day attribution window captures >95% of meaningful touchpoints in the buyer journey

### Constraints
- Ad platform APIs have 24-48 hour data delays — attribution data will always be T+2 at best for paid channels
- Cross-device identity resolution is not solved — relying on logged-in user email matching only
- LinkedIn Ads API has rate limits that constrain historical backfill to 6 months
- Data-driven model requires minimum 6 months of data before it produces reliable results (last-touch used as fallback initially)

---

## 10. Risks & Open Questions

### Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Identity stitching match rate below 85% | High — large portion of touchpoints unattributed | Medium | Implement fuzzy matching fallback; cookie-based stitching for web |
| UTM tagging inconsistency across teams | High — touchpoints miscategorized by channel | High | Publish UTM standards; weekly compliance report; automated validation |
| Cookie/tracking deprecation (3P cookies, iOS changes) | High — web touchpoint volume drops | Medium | Invest in first-party data strategy; server-side tracking via Snowplow |
| Ad platform API rate limits during backfill | Low — delays historical data load | Medium | Implement exponential backoff; spread backfill over 2 weeks |
| Stakeholder disagreement on "which model is right" | Medium — delays adoption | High | Present all 4 models simultaneously; let data-driven model earn trust over time |

### Open Questions

| Question | Owner | Due Date | Status |
|---|---|---|---|
| What is the current UTM tagging compliance rate across paid channels? | Marketing Ops | 2026-04-20 | Open |
| Should offline events (conferences) be included in the touchpoint timeline? | CMO | 2026-04-25 | Open |
| What is the minimum viable identity match rate for the product to be useful? | Marketing Analytics | 2026-04-30 | Open |
| How should "direct/organic" conversions (no marketing touchpoints) be handled in the model? | Data Science | 2026-05-01 | Open |

---

## 11. Milestones & Rollout

### Timeline

| Phase | Description | Target Date | Exit Criteria |
|---|---|---|---|
| Discovery | Requirements finalized, source access confirmed, UTM audit complete | Week 1-2 | PRD approved, baseline UTM compliance measured |
| Build — Identity | Identity stitching pipeline, UTM parsing, touchpoint assembly | Week 3-5 | >85% identity match rate, touchpoint timeline validated |
| Build — Attribution | Four attribution models, revenue matching, dashboard tables | Week 6-8 | All models producing results, revenue reconciliation within ±2% |
| Validate | UAT with Marketing Ops analyst + 2 channel managers | Week 9-10 | Stakeholder sign-off, numbers reviewed against manual analysis |
| Launch | Production deployment, dashboards live | Week 11 | SLA met for 5 consecutive days |
| Iterate | Feedback, model tuning, UTM compliance improvements | Week 12-16 | CMO uses data for Q4 budget allocation |

### Launch Criteria
- [ ] All four attribution models producing results
- [ ] Revenue reconciliation within ±2% for each model
- [ ] Identity stitching match rate > 85%
- [ ] SLA met for 5+ consecutive days
- [ ] Marketing Ops analyst validated against previous manual analysis
- [ ] Monitoring and alerting configured
- [ ] UTM compliance report operational
- [ ] Documentation published in data catalog

---

## Appendix

### Glossary
| Term | Definition |
|---|---|
| Multi-Touch Attribution (MTA) | A method of assigning conversion credit to multiple marketing touchpoints in the buyer journey, rather than just the first or last touch |
| ROAS | Return on Ad Spend — revenue attributed to a channel or campaign divided by its cost |
| Time-Decay Attribution | An attribution model that assigns exponentially more credit to touchpoints closer to the conversion event |
| Shapley Value | A game theory concept used in data-driven attribution to fairly distribute credit based on each touchpoint's marginal contribution |
| Identity Stitching | The process of linking anonymous and known user interactions across systems into a unified contact profile |
| Attribution Window | The maximum lookback period for touchpoints to be considered part of a conversion journey (default: 90 days) |

### Sample Output
| channel | campaign_name | attribution_model | attributed_revenue | cost | roas | conversions | avg_touchpoints |
|---|---|---|---|---|---|---|---|
| paid_search | Brand_Keywords_Q2 | time_decay | $185,400 | $42,000 | 4.41 | 234 | 3.2 |
| email | Nurture_Series_Enterprise | time_decay | $312,000 | $8,500 | 36.71 | 89 | 5.1 |
| paid_social | LinkedIn_ABM_Campaign | time_decay | $94,200 | $35,000 | 2.69 | 41 | 4.8 |
| content | Blog_SEO_Organic | time_decay | $156,800 | $12,000 | 13.07 | 156 | 2.4 |

### References
- Marketing Budget Allocation FY2027 — CMO Planning Document
- UTM Tagging Standards — Marketing Ops Playbook
- Attribution Modeling Best Practices — Google/Meta documentation
- ABM Program Business Case — VP Marketing Proposal
""",
    },
}
