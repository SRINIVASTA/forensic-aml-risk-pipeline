import pandas as pd
import numpy as np

def process_kyc_pipeline(df_raw_clients):
    """Clean data structures and execute structural compliance risk metrics."""
    df = df_raw_clients.copy()
    
    if 'beneficial_owners' not in df.columns:
        df['beneficial_owners'] = [[] for _ in range(len(df))]
    else:
        df['beneficial_owners'] = df['beneficial_owners'].apply(
            lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else ([x] if pd.notna(x) else [])
        )
        
    results = df.apply(calculate_onboarding_risk, axis=1)
    df[['Risk_Score', 'Risk_Rating', 'Flags_Triggered', 'KYC_Status']] = results
    return df

def rapid_levenshtein_ratio(s1, s2):
    """Calculates an optimized Levenshtein distance using structural pruning."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]

def calculate_onboarding_risk(row):
    """Evaluates multi-vector regulatory risks to yield risk metrics and operational status."""
    risk_score = 0
    flags = []
    
    HIGH_RISK_COUNTRIES = {"Iran", "North Korea", "Syria", "Myanmar", "Russia", "RU"}
    PEP_LIST = {"john doe sr.", "jane smith-vip", "alex president"}
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
            for sub_element in element: 
                extract_strings(sub_element)
        elif pd.notna(element):
            val = str(element).strip()
            if val: 
                flat_owners.append(val.lower())
                
    extract_strings(row.get('beneficial_owners', []))
            
    for individual_name in flat_owners:
        if individual_name in {"undisclosed owner", "none", ""}:
            continue
            
        for pep in PEP_LIST:
            if abs(len(individual_name) - len(pep)) > FUZZY_MATCH_THRESHOLD:
                continue
                
            if rapid_levenshtein_ratio(individual_name, pep) <= FUZZY_MATCH_THRESHOLD:
                pep_flags.append(f"{individual_name.title()} (Matched: {pep.title()})")
                break
                
    if pep_flags or pep_flag == 1:
        risk_score += 40
        flags.append(f"PEP Alert: {', '.join(pep_flags) if pep_flags else 'Direct Flag'}")

    if risk_score >= 50:
        rating, status = "High Risk", "Escalate for EDD"
    elif risk_score >= 20:
        rating, status = "Medium Risk", "Requires Bi-Annual Review"
    else:
        rating, status = "Low Risk", "Approved"
        
    return pd.Series([risk_score, rating, ", ".join(flags) if flags else "None", status])
