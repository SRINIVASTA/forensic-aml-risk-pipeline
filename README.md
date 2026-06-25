# 🛡️ Forensic KYC/AML Compliance Suite

A high-density, automated financial intelligence surveillance engine built with **Streamlit** and **Python 3.14**. This suite provides multi-vector compliance analysis across incoming real-time cash streams and static customer registries to instantly isolate money laundering, sanctions evasion, and political exposure risks.

---

## 📈 Architecture & System Topography

The software is decoupled into an explicit 4-way functional modular pipeline framework:

```text
├── app.py                      # Core UI State Machine & Modality Orchestrator
├── requirements.txt
└── engines/
    ├── __init__.py             # Empty structural package marker
    ├── kyc_engine.py           # Fuzzy String Matchers & Onboarding Risk Core
    ├── aml_engine.py           # Isolation Forest ML Engine & Country Corridors
    └── reporting_engine.py     # High-Performance In-Memory PDF & Excel Serializer
```

### 🧱 Component Matrix Breakdown

#### 1. `app.py`
The system orchestrator. It manages user settings, handles file uploads, drives rendering container targets, and binds streaming tickers. It features persistent browser session tracking (`st.session_state`) to guarantee that your execution logs and analytics visual arrays never drop from memory when report action switches are toggled.

#### 2. `kyc_engine.py`
Drives individual entity verification checking. It utilizes a highly optimized space-efficient 2-row rolling **Levenshtein Distance Ratio** algorithm to perform fuzzy name screening against Politically Exposed Persons (PEP) matrices, short-circuiting lookup computations if string length deviations violate pruning criteria.

#### 3. `aml_engine.py`
Evaluates algorithmic transaction flow patterns. It passes financial quantities into an **Isolation Forest Machine Learning Outlier Classifier** configured to separate anomalies at an optimized 1% boundary. Simultaneously, it evaluates high-threat offshore corridors (`KY`, `BM`, `CY`, etc.) and handles raw data column alignments.

#### 4. `reporting_engine.py`
The core document factory. It generates comprehensive compliance dossiers on demand. It pipes formatted ledger data frames directly to an in-memory binary stream buffer (`io.BytesIO`) using `fpdf2` and `openpyxl`. This avoids the file system, fixing protocol errors and layout drops under Python 3.14.

---

## ⚡ Deployment & Quickstart

### 📥 1. Clone & Structure Parity
Ensure your code layout exactly reflects the package framework below:
```bash
git clone https://github.com
cd forensic-aml-risk-pipeline
```

### 📦 2. Configure Local Environment Variables
Create a `requirements.txt` file in the main root directory of the application:
```text
streamlit
pandas
numpy
scikit-learn
fpdf2
openpyxl
matplotlib
```

Install your required dependencies through your preferred terminal shell:
```bash
pip install -r requirements.txt
```

### 🚀 3. Booting the Application
Launch the local verification server instance with the following execution call:
```bash
streamlit run app.py
```

---

## 🛠️ Modality Operational Workflows

*   **⚡ Real-Time Live Data Stream**: Simulates direct global SWIFT/ACH transaction transmissions. If data streams break or skip, use the custom sidebar **Reset Live Simulation History** button to purge the session cache registry and clear out metrics arrays for fresh testing.
*   **📄 Static CSV Uploads**: Accepts complete batch files (`clients.csv` and `transactions.csv`). It maps column aliases dynamically, surfaces risk category distribution charts, and exports separated high-risk case worksheets instantly.

---

## 🛡️ Data Compliance Standards Matrix
*   **OFAC / FATF Sanctions**: Instant matching filters flagging high-threat jurisdictions.
*   **Corridor Routing Risks**: Isolated filters tracking funds flowing out of standard sovereign entities into known offshore asset tax havens.
*   **Cognitive Anomaly Trees**: Unsupervised isolation forest model processing to stop structural structuring velocity spikes.

---

## ✒️ Author & Intellectual Property
Created and maintained by **Srinivasta**. All rights reserved.
