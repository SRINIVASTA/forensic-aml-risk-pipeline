import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def process_aml_pipeline(df_aml_raw, df_processed_clients):
    df_aml = df_aml_raw.copy()
    
    def extract_column(df, choices):
        for choice in choices:
            if choice in df.columns: return df[choice]
        return 0

    df_aml['ofac_match_clean'] = extract_column(df_aml, ['ofac_match', 'ofac_country'])
    df_aml['fatf_country_clean'] = extract_column(df_aml, ['fatf_country'])
    df_aml['structuring_clean'] = extract_column(df_aml, ['structuring', 'structuring_flag'])
    df_aml['rapid_movement_clean'] = extract_column(df_aml, ['rapid_movement', 'velocity_spike'])
    df_aml['trade_mispricing_clean'] = extract_column(df_aml, ['trade_mispricing_flag', 'mispricing_flag'])

    OFFSHORE_HAVENS = ["KY", "BM", "CY", "VG", "PA", "BS"]
    df_aml['corridor_risk_clean'] = df_aml.apply(
        lambda r: 1 if r.get('counterparty_country') in OFFSHORE_HAVENS and r.get('client_country') not in OFFSHORE_HAVENS else 0, axis=1
    )

    # Train Isolation forest model with the fine-tuned 1% anomaly cap
    X_ml = df_aml[['amount']].values
    iso_forest = IsolationForest(contamination=0.01, random_state=42)
    df_aml['ML_Anomaly_Score'] = iso_forest.fit_predict(X_ml)
    df_aml['ML_Profiling'] = df_aml['ML_Anomaly_Score'].apply(lambda x: "⚠️ OUTLIER DETECTED" if x == -1 else "NORMAL")

    # Perform SQL-equivalent lookup relational merge
    df_master = df_aml.merge(df_processed_clients, on="client_id", how="left")

    df_flagged = df_master[
        (df_master['ofac_match_clean'] == 1) | (df_master['fatf_country_clean'] == 1) | 
        (df_master['structuring_clean'] == 1) | (df_master['rapid_movement_clean'] == 1) | 
        (df_master['trade_mispricing_clean'] == 1) | (df_master['corridor_risk_clean'] == 1) |
        (df_master['ML_Profiling'] == "⚠️ OUTLIER DETECTED")
    ].copy()

    def resolve_aml_status(row):
        flags = []
        if row['ofac_match_clean'] == 1: flags.append("OFAC Match")
        if row['fatf_country_clean'] == 1: flags.append("FATF Blacklist")
        if row['structuring_clean'] == 1: flags.append("Structuring")
        if row['rapid_movement_clean'] == 1: flags.append("Velocity Spike")
        if row['trade_mispricing_clean'] == 1: flags.append("Mispricing")
        if row['corridor_risk_clean'] == 1: flags.append("Corridor Deviation")
        if row['ML_Profiling'] == "⚠️ OUTLIER DETECTED": flags.append("ML Anomaly")
        return " | ".join(flags) if flags else "CLEAN"

    if not df_flagged.empty:
        df_flagged['AML_Status'] = df_flagged.apply(resolve_aml_status, axis=1)
    else:
        df_flagged['AML_Status'] = pd.Series(dtype='str')

    return df_aml, df_flagged
