import pandas as pd

# This function detects unusual session durations in the dataset.
# It calculates the mean and standard deviation of session_duration_minutes
# and flags any session more than 3 standard deviations above the mean as "Anomaly".
# This helps identify bot activity, idle sessions, or data entry errors
# that could affect analysis accuracy.

def anomaly_flag(df):
    mean = df['session_duration_minutes'].mean()
    std = df['session_duration_minutes'].std()
    df['session_anomaly'] = df['session_duration_minutes'].apply(
        lambda x: 'Anomaly' if x > mean + 3*std else 'Normal'
    )
    return df

def get_output_schema():
    return pd.DataFrame({
        'session_anomaly': prep_string()
    })