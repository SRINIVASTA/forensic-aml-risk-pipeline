# Safe dynamic FPDF interface fallback loader wrapper
try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    from fpdf2 import FPDF
    from fpdf2.enums import XPos, YPos

from datetime import datetime
import io
import pandas as pd

class CompliancePDFReport(FPDF):
    def header(self):
        self.set_fill_color(26, 54, 93)
        self.rect(0, 0, 210, 32, 'F')
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_y(10)
        self.cell(0, 10, 'FINANCIAL INTELLIGENCE COMPLIANCE UNIT', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_y(38)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'CONFIDENTIAL AUDIT DOSSIER | Page {self.page_no()}', align='C')

def compile_pdf_report(df_clients, df_aml, df_flagged_alerts):
    pdf = CompliancePDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 8, '1. Executive Summary Analysis', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, f"Execution Evaluation Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Total Ingested Core Clients     : {len(df_clients)} Active Entities", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Total Evaluated Flow Records   : {len(df_aml)} Transactions Checked", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_text_color(199, 44, 44)
    pdf.cell(0, 6, f"Isolated Anomalous High-Risks  : {len(df_flagged_alerts)} Cases Escalated", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 8, '2. Escalated Forensic Incident Logs (Top 20 Critical Vectors)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_fill_color(230, 235, 245)
    pdf.set_text_color(26, 54, 93)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(25, 7, 'Client ID', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(35, 7, 'Transaction ID', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(35, 7, 'Amount Value', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(95, 7, 'Primary Flag Risk Signals Captured', border=1, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 0, 0)
    
    if not df_flagged_alerts.empty:
        for _, row in df_flagged_alerts.head(20).iterrows():
            pdf.cell(25, 6, str(row.get('client_id', 'N/A')), border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(35, 6, str(row.get('transaction_id', row.get('tx_id', 'N/A'))), border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(35, 6, f"${float(row.get('amount', 0)):,.2f}", border=1, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
            
            status_text = str(row.get('AML_Status', 'ML Anomaly'))
            if len(status_text) > 52:
                status_text = status_text[:49] + "..."
            pdf.cell(95, 6, status_text, border=1, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(190, 10, 'No anomalies isolated across data arrays during evaluation window.', border=1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return pdf.output()

# FIXED: Synchronized signature to accept 3 parameters to prevent frontend layout crashes
def compile_excel_workbook(df_clients, df_aml, df_flagged_alerts):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_clients.to_excel(writer, sheet_name='KYC_Master_Registry', index=False)
        df_aml.to_excel(writer, sheet_name='AML_Transaction_Ledger', index=False)
        df_flagged_alerts.to_excel(writer, sheet_name='Isolated_Compliance_Alerts', index=False)
    return excel_buffer.getvalue()
