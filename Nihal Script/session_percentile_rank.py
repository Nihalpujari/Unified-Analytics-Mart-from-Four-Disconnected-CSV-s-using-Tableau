import pandas as pd
from scipy import stats

# This function calculates the percentile rank of each session
# based on session_duration_minutes across the entire dataset.
# A score of 95 means that session is longer than 95% of all sessions.
# This is impossible in Tableau natively as it requires a true
# dataset-wide ranking using scipy, not a view-dependent table calc.

def session_percentile_rank(df):
    df['session_percentile_rank'] = df['session_duration_minutes'].apply(
        lambda x: round(stats.percentileofscore(df['session_duration_minutes'], x, kind='rank'), 2)
    )
    return df

def get_output_schema():
    return pd.DataFrame({
        'session_percentile_rank': prep_decimal()
    })
