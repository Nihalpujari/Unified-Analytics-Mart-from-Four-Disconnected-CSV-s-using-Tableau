import pandas as pd

# This function scans every column in the dataset and outputs
# a summary of null/missing values per field.
# For each column it returns: the column name, total row count,
# number of nulls, and the null percentage.
# This is structurally impossible in Tableau — it cannot transform
# column-level metadata into rows for auditing purposes.
# Use this as a separate Prep branch before your main flow
# to catch data quality issues early.

def missing_value_audit(df):
    total_rows = len(df)
    audit_rows = []

    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = round((null_count / total_rows) * 100, 2)
        audit_rows.append({
            'column_name': col,
            'total_rows': total_rows,
            'null_count': int(null_count),
            'null_percentage': null_pct
        })

    return pd.DataFrame(audit_rows)

def get_output_schema():
    return pd.DataFrame({
        'column_name':    prep_string(),
        'total_rows':     prep_int(),
        'null_count':     prep_int(),
        'null_percentage': prep_decimal()
    })
