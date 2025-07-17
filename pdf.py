import os
import tempfile
from fpdf import FPDF
import plotly.io as pio

def generate_pdf(df, fig1, fig2, filename, total_original, total_balanced, function_detail):
    # Create a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save charts as images using Plotly's to_image (NO Kaleido required)
        fig1_path = os.path.join(tmpdir, "original_chart.png")
        fig2_path = os.path.join(tmpdir, "balanced_chart.png")

        # Export figures as PNG
        fig1_bytes = pio.to_image(fig1, format="png", width=900, height=600)
        with open(fig1_path, "wb") as f:
            f.write(fig1_bytes)

        fig2_bytes = pio.to_image(fig2, format="png", width=900, height=600)
        with open(fig2_path, "wb") as f:
            f.write(fig2_bytes)

        # Convert dataframe to text format
        df_text = df.to_string(index=False)

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, f"Bar Chart Balancing Report - {filename}", ln=True, align="C")

        # Data Table
        pdf.set_font("Arial", "", 16)
        pdf.ln(10)
        pdf.cell(0, 10, "Original vs Balanced Values:", ln=True)

        pdf.set_font("Courier", "", 14)
        for line in df_text.split('\n'):
            pdf.multi_cell(0, 5, line)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{function_detail}", ln=True)

        # Charts
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Original Input Bar Chart", ln=True)
        pdf.image(fig1_path, w=180)
        pdf.cell(0, 10, f"Total Original Value: {total_original}", ln=True)

        pdf.add_page()
        pdf.ln(10)
        pdf.cell(0, 10, "Balanced Bar Chart", ln=True)
        pdf.image(fig2_path, w=180)

        # Summary Metrics
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary Metrics:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Total Balanced Value: {total_balanced}", ln=True)

        # Save PDF to a buffer
        pdf_path = os.path.join(tmpdir, f"{filename}-report.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            return f.read()
