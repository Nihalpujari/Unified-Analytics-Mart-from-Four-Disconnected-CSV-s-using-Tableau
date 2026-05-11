# 🛒 Unified Analytics Mart from Four Disconnected CSVs

> **Cleaning, Transforming, and Integrating E-Commerce Data with Tableau Prep and Python**

A Data Management project by students of the **M.Sc. Applied Data Science & Artificial Intelligence** program at **SRH University Heidelberg**.

---

## 👥 Team

| Name | Role |
|------|------|
| Namrata Bhoyar | Team Member |
| Anuj Kamble | Team Member |
| Gourav Somanna | Team Member |
| Nihal Pujari | Team Member |
| Pramodkumar Shivanna | Team Member |

---

## 📌 Problem Statement

Four isolated CSV files — each capturing one business dimension — could not answer cross-functional questions on their own.

| Business Question | Description |
|---|---|
| **PS1** | Which membership tier buys high-return products in worst revenue months? |
| **PS2** | Which age group stops purchasing during revenue dips? |
| **PS3** | Is heavy discounting hurting monthly revenue? |

---

## 📂 Dataset

**Source:** Kaggle.com — E-Commerce Dataset 2020–2026  
**Domain:** E-commerce business operations & retail analytics  
**Format:** 4 separate CSV files · ~33,000 total records

| File | Rows | Columns | Content |
|------|------|---------|---------|
| `customers.csv` | 8,000 | 20 | Demographics, membership tier, spending behavior, churn |
| `orders.csv` | 25,000 | 28 | Transaction-level data, payment, delivery, ratings |
| `product_summary.csv` | 140 | 9 | Product performance metrics, ratings, return rates |
| `monthly_revenue.csv` | 75 | 10 | Monthly aggregated business KPIs and revenue trends |

---

## 🏗️ Flow Architecture — Six Stages

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
  │           │          │         │          │         │
Load      Independent  Split &   Joins     Pivot     Python
raw       cleaning     union     for PS    wide→     script
data      per source   (order_   masters   long      integration
                       health)
```

**35+ transformation steps · 4 source CSV files · 4 master output datasets**

---

## 🧹 Data Issues Found & Fixed

| Dataset | Issues |
|---------|--------|
| `monthly_revenue` | Duplicate rows · quarter stored as Q1/q1/Quarter 1/QTR1 · revenue as text `"$42,000"` · null discount + return_rate values |
| `orders` | 50 injected duplicate rows · `delivery_days = -5` (impossible) · negative `unit_price_usd` · month stored as text |
| `customers` | 400 missing values each in age, country, gender · country written as DEU/GER/USA/U.S.A. · `registration_date` in 6 mixed formats |
| `product_summary` | Category inconsistency (`'Apparel'` vs `'Clothing & Apparel'`) · leading/trailing/internal whitespace in `product_name` |

---

## ⚙️ Selected Transformation Highlights

| Technique | Detail |
|-----------|--------|
| **Duplicate detection** | `ROW_NUMBER()` partitioned across all columns; keep `'Unique'` rows only |
| **Standardization** | Remap quarter (Q1/q1/QTR1 → Q1); country (DEU → GERMANY); `UPPER()` |
| **Type cleanup** | `FLOAT(REPLACE(revenue_usd, '$', ''))` — string → numeric |
| **Whitespace fix** | `REGEXP_REPLACE` on `product_name` to handle leading/trailing/internal spaces |
| **Range filters** | `delivery_days ≠ -5`; `rating ∈ [1,5]`; `return_rate ∈ [0,100]` |
| **Derived fields** | `year_month`, `revenue_per_customer`, `retention_rate_pct`, `order_value_tier` |
| **Integrity checks** | Subtotal vs `unit_price × quantity`; total vs sum of components |

### Before vs After — Key Examples

| Column / Step | BEFORE (dirty) | AFTER (clean) |
|---|---|---|
| `quarter` | Q1 / q1 / Quarter 1 / QTR1 | Q1 (one consistent value) |
| `country` | DEU / GER / germany / GERMANY | GERMANY (uppercased, remapped) |
| `revenue_usd` | `"$42,000"` (stored as text) | `42000.0` (numeric decimal) |
| `product_name` | `" Running Shoes "` (with spaces) | `"Running Shoes"` (trimmed) |
| `order_health` | Not present — buried in 2 columns | `"Healthy"` or `"At Risk"` (new flag) |
| `session_in_hours` | Not present — only `session_duration_minutes` | `1.35 hrs` (derived + renamed) |

---

## 🔗 Joins Strategy

Three different join types, each chosen for a documented business reason:

| Join Type | Tables | Key | Reason |
|-----------|--------|-----|--------|
| **INNER JOIN** | Orders ↔ Customers | `customer_id` | Drop orders with unknown customers — they cannot be analyzed |
| **LEFT JOIN** | Result ↔ Product Summary | `product_name + category` | Keep all orders even if product is not in the summary yet |
| **INNER JOIN** | Result ↔ Monthly Revenue | `year + month` | Every order belongs to a month for which revenue is recorded |

---

## 🔀 Union — Engineering a New Feature Column

The `order_health` signal was buried across two columns (`order_status` and `returned`). Splitting orders into two filtered branches, tagging each, then unioning them creates one clean categorical column that did not exist in the source.

```
Cleaned Orders
     ├── Healthy Orders  →  order_health = "Healthy"
     └── At Risk Orders  →  order_health = "At Risk"
              └── UNION → Orders_Tagged
```

Every order now carries a single `order_health` flag that all downstream joins inherit.

---

## 📊 Pivot — Wide Format to Long Format

The monthly revenue table was pivoted from wide to long format so analysts can build a single dashboard with a metric dropdown filter — any KPI can be charted without rebuilding the worksheet.

```
BEFORE (wide):  year | month | revenue | AOV | return%
AFTER (long):   year | month | metric_name | metric_value
```

---

## 🐍 Python Script Integration (Stage 6)

Three custom Python scripts extend what Tableau Prep cannot do natively:

### Script 1 — `anomaly_flag.py`
Flags sessions where `session_duration_minutes` is statistically unusual using z-scores (mean ± 3σ). Tableau Prep cannot compute z-scores or perform statistical outlier detection natively.

```python
def anomaly_flag(df):
    mean = df['session_duration_minutes'].mean()
    std  = df['session_duration_minutes'].std()
    df['session_anomaly'] = df['session_duration_minutes'].apply(
        lambda x: 'Anomaly' if x > mean + 3*std else 'Normal'
    )
    return df
```

### Script 2 — `session_percentile_rank.py`
Scores every session 0–100 based on how its duration compares to the full dataset using `scipy.stats.percentileofscore`. Tableau's `RANK()` is view-dependent and cannot produce a fixed, dataset-wide score.

```python
def session_percentile_rank(df):
    df['session_percentile_rank'] = df['session_duration_minutes'].apply(
        lambda x: round(stats.percentileofscore(
            df['session_duration_minutes'], x, kind='rank'), 2)
    )
    return df
```

### Script 3 — `missing_value_audit.py`
Scans every column and outputs one summary row per field showing `column_name`, `total_rows`, `null_count`, and `null_percentage`. Structurally impossible in Tableau — it cannot loop over column names as values or collapse a dataset into column-level summary rows.

```python
def missing_value_audit(df):
    total_rows = len(df)
    audit_rows = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct   = round((null_count / total_rows) * 100, 2)
        audit_rows.append({
            'column_name':    col,
            'total_rows':     total_rows,
            'null_count':     int(null_count),
            'null_percentage': null_pct
        })
    return pd.DataFrame(audit_rows)
```

---

## 💡 Insights

### Marketing
- Basic-tier customers buy more high-return products in bad revenue months
- **Solution:** Run quality-focused campaigns for this group in weak months

### Sales
- Age group 26–35 stops buying first when revenue drops
- **Solution:** Target this age group with reactivation campaigns during dips

### Finance
- Products with 40%+ discounts = lower revenue + more returns
- **Solution:** Stop heavy discounting — redirect that budget elsewhere

---

## 📈 Flow Comparison

| | Before | After |
|---|---|---|
| **Data state** | 4 separate CSV files with no connection | Separate cleaned output tables per business question |
| **Analysis method** | Manual VLOOKUPs in Excel — often crashed | Open the right output, apply filters — done |
| **Time to insight** | 2–3 hours per business question | ~5 minutes |
| **Refresh** | Redo everything from scratch each month | Flow reruns automatically with new data |
| **Trust** | Each team worked from different versions | All teams use the same cleaned, trusted data |

---

## 🔬 FAIR Data Compliance

| Principle | Implementation |
|-----------|---------------|
| **Findable** | Every output table named by its purpose; column names are clear and self-explanatory |
| **Accessible** | Output saved as standard CSV/hyper file; no special software required |
| **Interoperable** | All formats standardized — dates, country names, quarter labels; data types are correct; join keys consistent across all tables |
| **Reusable** | Tableau Prep flow is documented and saved; new data flows through the same pipeline without changes |

---

## 🗂️ Repository Structure

```
├── Flow.tfl                          # Tableau Prep Builder flow file
├── customers.csv                     # Source: customer demographics & behavior
├── orders.csv                        # Source: transaction-level order data
├── product_summary_dirty.csv         # Source: product performance metrics
├── monthly_revenue_dirty.csv         # Source: monthly aggregated KPIs
├── anomaly_flag.py                   # Python script: session anomaly detection
├── session_percentile_rank.py        # Python script: dataset-wide percentile rank
├── missing_value_audit.py            # Python script: null value audit per column
└── Tableau_Prep_Project_Presentation.pdf  # Full project presentation
```

---

## 🛠️ Requirements

- **Tableau Prep Builder** (to run the `.tfl` flow)
- **Python 3.x** with the following packages for the script steps:
  ```
  pandas
  scipy
  ```

---

*SRH University Heidelberg · M.Sc. Applied Data Science & Artificial Intelligence · Course: Data Management*
