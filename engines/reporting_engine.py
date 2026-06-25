from fpdf import FPDF  # DO NOT USE fpdf2 HERE - fpdf2 is imported as 'fpdf'
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

def compile_excel_workbook(df_clients, df_aml, df_flagged_alerts):
    """Assembles a multi-sheet tracking ledger buffer containing full compliance records."""
    import io
    import pandas as pd
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_clients.to_excel(writer, sheet_name='KYC_Master_Registry', index=False)
        df_aml.to_excel(writer, sheet_name='AML_Transaction_Ledger', index=False)
        df_flagged_alerts.to_excel(writer, sheet_name='Isolated_Compliance_Alerts', index=False)
    return excel_buffer.getvalue()
