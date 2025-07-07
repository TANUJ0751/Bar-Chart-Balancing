from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os


def generate_pdf(df, fig1, fig2, filename, total_original, total_balanced):
    # Create a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save charts as images
        fig1_path = os.path.join(tmpdir, "original_chart.png")
        fig2_path = os.path.join(tmpdir, "balanced_chart.png")

        fig1.write_image(fig1_path, format='png', engine='kaleido')
        fig2.write_image(fig2_path, format='png', engine='kaleido')

        # Convert dataframe to text format
        df_text = df.to_string(index=False)

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Bar Chart Balancing Report", ln=True, align="C")

        # Data Table
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, "Original vs Balanced Values:", ln=True)

        pdf.set_font("Courier", "", 9)
        for line in df_text.split('\n'):
            pdf.multi_cell(0, 5, line)

        # Charts
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Original Input Bar Chart", ln=True)
        pdf.image(fig1_path, w=180)

        pdf.ln(10)
        pdf.cell(0, 10, "Balanced Bar Chart", ln=True)
        pdf.image(fig2_path, w=180)

        # ➕ Add Variable Values Here
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary Metrics:", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Total Original Value: {total_original}", ln=True)
        pdf.cell(0, 10, f"Total Balanced Value: {total_balanced}", ln=True)

        # Save PDF to a buffer
        pdf_path = os.path.join(tmpdir, f"{filename}-report.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            return f.read()