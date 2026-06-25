import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Centralized Imports straight from our engine module library folder package
from engines.kyc_engine import process_kyc_pipeline
from engines.aml_engine import process_aml_pipeline
from engines.reporting_engine import compile_pdf_report, compile_excel_workbook

st.set_page_config(page_title="Forensic KYC/AML Automation Suite", layout="wide")

st.title("🛡️ Centralized Forensic KYC/AML Compliance Suite")
st.markdown("Modular Enterprise Architecture: Independent Processing Engines Routed Through a Central Control Dashboard.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("📁 Step 1: Ingest Client Registry")
    uploaded_clients_file = st.file_uploader("Upload clients.csv", type=["csv"])
with col2:
    st.subheader("💳 Step 2: Ingest Transaction Ledger")
    uploaded_tx_file = st.file_uploader("Upload transactions.csv", type=["csv"])

if uploaded_clients_file and uploaded_tx_file:
    # 1. Ingest clean data frames via streams
    df_clients_raw = pd.read_csv(uploaded_clients_file)
    df_aml_raw = pd.read_csv(uploaded_tx_file)
    
    # 2. Route straight out into block 1 KYC calculation engine
    df_clients = process_kyc_pipeline(df_clients_raw)
    
    # 3. Route datasets out into block 2 AML streaming engine
    df_aml, df_flagged_alerts = process_aml_pipeline(df_aml_raw, df_clients)
    
    # Render Streamlit Display Framework View layout tabs
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
        colors = ['#bdc3c7' if v==0 else '#e74c3c' for v in series_metrics.values]
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
        
        # Call block 3 centralized reporting engines
        pdf_data = compile_pdf_report(df_clients, df_aml, df_flagged_alerts)
        excel_data = compile_excel_workbook(df_clients, df_aml)
        
        st.download_button(label="📥 Download Signed PDF Compliance Report", data=pdf_data, file_name="Forensic_Audit_Report.pdf", mime="application/pdf")
        st.download_button(label="📥 Download Multi-Sheet Excel Ledger Book", data=excel_data, file_name="Compliance_Audit_Trail.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
