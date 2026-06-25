import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import random
from datetime import datetime

# Import centralized modular functional packages from engines/ directory
from engines.kyc_engine import process_kyc_pipeline
from engines.aml_engine import process_aml_pipeline
from engines.reporting_engine import compile_pdf_report, compile_excel_workbook

st.set_page_config(page_title="Forensic KYC/AML Compliance Suite", layout="wide")

# =====================================================================
# SIDEBAR CONTROLS
# =====================================================================
st.sidebar.title("🛡️ Compliance Engine Settings")
st.sidebar.markdown("Configure how data is piped into the forensic execution core.")

# Modality Ordering: Live stream is Option 1, File Upload is Option 2
app_mode = st.sidebar.radio(
    "Choose Data Ingestion Pipeline Mode:",
    ["⚡ Real-Time Live Data Stream", "📄 Static CSV Uploads"]
)

if "live_ledger" not in st.session_state:
    st.session_state.live_ledger = []
if "tick_counter" not in st.session_state:
    st.session_state.tick_counter = 0

# FIXED: Fully populated arrays to eliminate AST parsing failures
mock_clients_raw = pd.DataFrame({
    "client_id": [1137, 716, 772, 681, 402],
    "client_name": ["Wells-Turner Corp", "Goodman Import LLC", "Phillips-Harris NGO", "Kim Anderson Defense", "Alpha Trading Co"],
    "sector_risk": ["High", "Medium", "High", "High", "Low"],
    "pep_flag": [0, 0, 1, 1, 0],
    "country": ["JP", "CH", "AE", "RU", "AU"],
    "sanctions_fatf_country": [0, 0, 1, 0, 0],
    "ofac_country": [0, 0, 0, 1, 0],
    "ownership_opacity_score": [0.0, 0.0, 0.5, 0.0, 0.0]
})

# =====================================================================
# MODALITY WORKFLOW 1: REAL-TIME STREAMING DATA ENGINE
# =====================================================================
if app_mode == "⚡ Real-Time Live Data Stream":
    st.title("⚡ Real-Time Streaming Data Surveillance Console")
    st.markdown("Simulating live global transactions. The interface automatically feeds items into the modular compliance architecture.")
    
    df_clients = process_kyc_pipeline(mock_clients_raw)
    run_stream = st.checkbox("▶️ Activate Live Streaming Wire Transmissions", value=False)
    
    status_placeholder = st.empty()
    chart_placeholder = st.empty()
    table_placeholder = st.empty()
    
    if run_stream:
        status_placeholder.info("Active Wire Feed: Streaming transactions, running Isolation Forest profiling...")
        
        while st.session_state.tick_counter < 30:
            st.session_state.tick_counter += 1
            tick = st.session_state.tick_counter
            
            # FIXED: Assigned explicit integer list choices to prevent execution crashes
            pool_clients = [1137, 716, 772, 681, 402]
            chosen_client = random.choice(pool_clients)
            
            # Inject explicit multi-vector rule scenarios dynamically to target exact records
            if tick == 5:
                chosen_client = 772
                amount = 145000.00
                ofac, fatf, struct, velocity, mispricing = 0, 1, 0, 1, 1
            elif tick in [12, 13, 14]:
                chosen_client = 681
                amount = 9950.00
                ofac, fatf, struct, velocity, mispricing = 1, 0, 1, 1, 0
            else:
                amount = round(random.uniform(250.00, 8500.00), 2)
                ofac, fatf, struct, velocity, mispricing = 0, 0, 0, 0, 0
                
            new_tx = {
                "transaction_id": f"TX_LIVE_{1000 + tick}",
                "client_id": chosen_client,
                "amount": amount,
                "transaction_type": random.choice(["SWIFT", "Wire", "ACH"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "client_country": "RU" if chosen_client == 681 else "IN",
                "counterparty_country": "KY" if tick == 5 else random.choice(["US", "SG", "NL"]),
                "ofac_match": ofac,
                "fatf_country": fatf,
                "structuring": struct,
                "rapid_movement": velocity,
                "trade_mispricing_flag": mispricing
            }
            
            st.session_state.live_ledger.append(new_tx)
            df_live_raw = pd.DataFrame(st.session_state.live_ledger)
            
            # Pipe streaming dataframe updates through the engines
            df_aml, df_flagged_alerts = process_aml_pipeline(df_live_raw, df_clients)
            
            with chart_placeholder.container():
                flag_metrics = {
                    'OFAC Matches': int(df_aml['ofac_match_clean'].sum()),
                    'FATF Blacklist': int(df_aml['fatf_country_clean'].sum()),
                    'Structuring': int(df_aml['structuring_clean'].sum()),
                    'Velocity Spike': int(df_aml['rapid_movement_clean'].sum()),
                    'Mispricing': int(df_aml['trade_mispricing_clean'].sum()),
                    'ML Outliers (1%)': int((df_aml['ML_Profiling'] == "⚠️ OUTLIER DETECTED").sum())
                }
                fig, ax = plt.subplots(figsize=(8, 2.5))
                pd.Series(flag_metrics).sort_values().plot(kind='barh', color=['#e74c3c' if v > 0 else '#bdc3c7' for v in pd.Series(flag_metrics).sort_values().values], ax=ax)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
            with table_placeholder.container():
                st.subheader("🔴 Live Compliance Case Desk (Flagged Surveillance Logs)")
                if not df_flagged_alerts.empty:
                    st.dataframe(df_flagged_alerts[['client_id', 'transaction_id', 'amount', 'AML_Status']].tail(10))
                else:
                    st.success("Monitoring system clear. Scanning network channels...")
                    
            time.sleep(0.3)
            
        status_placeholder.success("Simulation complete. Full log extraction arrays packaged.")
        pdf_data = compile_pdf_report(df_clients, df_aml, df_flagged_alerts)
        st.download_button(label="📥 Download Forensic Live Stream PDF Audit Report", data=pdf_data, file_name="Live_Stream_Forensic_Report.pdf", mime="application/pdf")
    else:
        status_placeholder.warning("Wire tracking link disconnected. Toggle the control switch to pipe incoming transmission signals.")

# =====================================================================
# MODALITY WORKFLOW 2: STATIC FILE UPLOADS LAYER
# =====================================================================
else:
    st.title("📄 File Ingestion & Forensic Processing Dashboard")
    st.markdown("Upload standard client and ledger registries directly into the verification matrix.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Phase 1: Client Registry")
        uploaded_clients = st.file_uploader("Upload clients.csv", type=["csv"])
    with col2:
        st.subheader("💳 Phase 2: Transaction Ledger")
        uploaded_tx = st.file_uploader("Upload transactions.csv", type=["csv"])

    if uploaded_clients and uploaded_tx:
        df_clients_raw = pd.read_csv(uploaded_clients)
        df_aml_raw = pd.read_csv(uploaded_tx)
        
        # Core modular execution routing
        df_clients = process_kyc_pipeline(df_clients_raw)
        df_aml, df_flagged_alerts = process_aml_pipeline(df_aml_raw, df_clients)
        
        tab1, tab2, tab3 = st.tabs(["📊 Analytics Metrics", "📑 Isolated Flagged Logs", "📥 Export Reports"])
        
        with tab1:
            st.subheader("Risk Category Trigger Frequency Distribution")
            flag_metrics = {
                'OFAC Matches': int(df_aml['ofac_match_clean'].sum()),
                'FATF Blacklist': int(df_aml['fatf_country_clean'].sum()),
                'Structuring': int(df_aml['structuring_clean'].sum()),
                'Velocity Spike': int(df_aml['rapid_movement_clean'].sum()),
                'Mispricing': int(df_aml['trade_mispricing_clean'].sum()),
                'Corridor Deviations': int(df_aml['corridor_risk_clean'].sum()),
                'ML Outliers (1%)': int((df_aml['ML_Profiling'] == "⚠️ OUTLIER DETECTED").sum())
            }
            fig, ax = plt.subplots(figsize=(8, 3.5))
            series_metrics = pd.Series(flag_metrics).sort_values()
            colors = ['#bdc3c7' if v == 0 else '#e74c3c' for v in series_metrics.values]
            series_metrics.plot(kind='barh', color=colors, edgecolor='black', ax=ax)
            st.pyplot(fig)

        with tab2:
            st.subheader("Forensic Case Management Audit Trail View")
            if not df_flagged_alerts.empty:
                st.dataframe(df_flagged_alerts[['client_id', 'transaction_id', 'amount', 'client_country', 'counterparty_country', 'AML_Status']].head(100))
            else:
                st.success("Clean batch processed. No compliance risks detected.")

        with tab3:
            st.subheader("Download Signed Compliance Artifact Documentation")
            pdf_data = compile_pdf_report(df_clients, df_aml, df_flagged_alerts)
            excel_data = compile_excel_workbook(df_clients, df_aml)
            
            st.download_button(label="📥 Download Signed PDF Compliance Report", data=pdf_data, file_name="Forensic_Audit_Report.pdf", mime="application/pdf")
            st.download_button(label="📥 Download Multi-Sheet Excel Ledger Book", data=excel_data, file_name="Compliance_Audit_Trail.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
