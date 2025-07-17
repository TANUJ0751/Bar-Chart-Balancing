from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import imgkit
import os


def generate_pdf(df, fig1, fig2, filename, total_original, total_balanced,function_detail):
    # Create a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save Plotly charts as HTML
        fig1_html = os.path.join(tmpdir, "original_chart.html")
        fig2_html = os.path.join(tmpdir, "balanced_chart.html")
        fig1.write_html(fig1_html)
        fig2.write_html(fig2_html)

        # Convert HTML charts to PNG using imgkit
        fig1_img = os.path.join(tmpdir, "original_chart.png")
        fig2_img = os.path.join(tmpdir, "balanced_chart.png")
        imgkit.from_file(fig1_html, fig1_img)
        imgkit.from_file(fig2_html, fig2_img)

        # Convert dataframe to text
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
        pdf.image(fig1_img, w=180)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Total Original Value: {total_original}", ln=True)

        pdf.add_page()
        pdf.cell(0, 10, "Balanced Bar Chart", ln=True)
        pdf.image(fig2_img, w=180)

        # Summary
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary Metrics:", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Total Balanced Value: {total_balanced}", ln=True)

        # Save PDF to buffer
        pdf_path = os.path.join(tmpdir, f"{filename}-report.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            return f.read()