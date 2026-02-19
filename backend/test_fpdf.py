from fpdf import FPDF
import os

print("Testing FPDF...")
try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(40, 10, "Hello World")
    
    reports_dir = os.path.abspath(os.path.join(os.getcwd(), "exports", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    out_path = os.path.join(reports_dir, "test_fpdf.pdf")
    
    pdf.output(out_path)
    print(f"FPDF Success: {out_path}")
except Exception as e:
    print(f"FPDF Error: {e}")
