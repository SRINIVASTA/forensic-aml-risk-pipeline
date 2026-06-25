import pandas as pd
import numpy as np

def dynamic_levenshtein_distance(str1, str2):
    m, n = len(str1), len(str2)
    dp = [list(range(n + 1)) if i == 0 else [i] + [0] * n for i in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]

def calculate_onboarding_risk(row):
    risk_score = 0
    flags = []
    HIGH_RISK_COUNTRIES = ["Iran", "North Korea", "Syria", "Myanmar", "Russia"]
    PEP_LIST = ["John Doe Sr.", "Jane Smith-VIP", "Alex President"]
    FUZZY_MATCH_THRESHOLD = 3
    
    country = str(row.get('country', row.get('client_country', 'US'))).strip()
    opacity = float(row.get('ownership_opacity_score', 0.0))
    pep_flag = int(row.get('pep_flag', 0))
    fatf_flag = int(row.get('sanctions_fatf_country', 0))
    ofac_flag = int(row.get('ofac_country', 0))
    
    if country in HIGH_RISK_COUNTRIES or fatf_flag == 1:
        risk_score += 50
        flags.append(f"High-Risk/FATF Jurisdiction ({country})")
    if ofac_flag == 1:
        risk_score += 50
        flags.append("OFAC Sanctions Match")
    if opacity > 0:
        risk_score += int(opacity * 30)
        flags.append("Opaque Ownership Structure")

    pep_flags = []
    flat_owners = []
    def extract_strings(element):
        if isinstance(element, (list, tuple, np.ndarray, pd.Series)):
            for sub_element in element: extract_strings(sub_element)
        else:
            if pd.notna(element): flat_owners.append(str(element).strip())
            
    if 'beneficial_owners' in row:
        extract_strings(row['beneficial_owners'])
            
    for individual_name in flat_owners:
        for pep in PEP_LIST:
            if dynamic_levenshtein_distance(individual_name.lower(), pep.lower()) <= FUZZY_MATCH_THRESHOLD:
                pep_flags.append(f"{individual_name} (Matched: {pep})")
                
    if pep_flags or pep_flag == 1:
        risk_score += 40
        flags.append(f"PEP Alert: {', '.join(pep_flags) if pep_flags else 'Direct Flag'}")

    rating = "High Risk" if risk_score >= 50 else ("Medium Risk" if risk_score >= 20 else "Low Risk")
    status = "Escalate for EDD" if risk_score >= 50 else ("Requires Bi-Annual Review" if risk_score >= 20 else "Approved")
    return pd.Series([risk_score, rating, ", ".join(flags) if flags else "None", status])

def process_kyc_pipeline(df_raw_clients):
    df = df_raw_clients.copy()
    if 'beneficial_owners' not in df.columns:
        df['beneficial_owners'] = "[['Undisclosed Owner']]"
    df[['Risk_Score', 'Risk_Rating', 'Flags_Triggered', 'KYC_Status']] = df.apply(calculate_onboarding_risk, axis=1)
    return df
