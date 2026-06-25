from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import io
import pandas as pd

class CompliancePDFReport(FPDF):
    def header(self):
        self.set_fill_color(26, 54, 93)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FINANCIAL INTELLIGENCE COMPLIANCE UNIT', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'CONFIDENTIAL AUDIT | Page {self.page_no()}', align='C')

def compile_pdf_report(df_clients, df_aml, df_flagged_alerts):
    pdf = CompliancePDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, '1. Executive Summary Details', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Execution Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Total Ingested Clients   : {len(df_clients)} Entities", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Total Evaluated Records  : {len(df_aml)} Transactions", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Total Flagged Anomalies  : {len(df_flagged_alerts)} Cases Isolated", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, '2. Escalated Forensic Case Registry', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(25, 7, 'Client ID', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(30, 7, 'Transaction ID', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(35, 7, 'Amount', border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(100, 7, 'Primary Flag Indicators Captured', border=1, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 9)
    for _, row in df_flagged_alerts.head(20).iterrows():
        pdf.cell(25, 6, str(row.get('client_id', 'N/A')), border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(30, 6, str(row.get('transaction_id', row.get('tx_id', 'N/A'))), border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(35, 6, f"${float(row.get('amount', 0)):,.2f}", border=1, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(100, 6, str(row['AML_Status'])[:55], border=1, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return pdf.output(dest='S').encode('latin-1') if isinstance(pdf.output(dest='S'), str) else pdf.output(dest='S')

def compile_excel_workbook(df_clients, df_aml):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_clients.to_excel(writer, sheet_name='KYC_Master_Registry', index=False)
        df_aml.to_excel(writer, sheet_name='AML_Transaction_Ledger', index=False)
    return excel_buffer.getvalue()
