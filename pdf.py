from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import imgkit
import os


def generate_pdf(df, fig1, fig2, filename, total_original, total_balanced,function_detail):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save charts as HTML first
        fig1_html_path = os.path.join(tmpdir, "fig1.html")
        fig2_html_path = os.path.join(tmpdir, "fig2.html")
        fig1.write_html(fig1_html_path)
        fig2.write_html(fig2_html_path)

        # Convert HTML to PNG
        fig1_img_path = os.path.join(tmpdir, "fig1.png")
        fig2_img_path = os.path.join(tmpdir, "fig2.png")
        imgkit.from_file(fig1_html_path, fig1_img_path)
        imgkit.from_file(fig2_html_path, fig2_img_path)

        # Continue your existing PDF logic
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, f"Bar Chart Balancing Report - {filename}", ln=True, align="C")

        df_text = df.to_string(index=False)
        pdf.set_font("Courier", "", 14)
        for line in df_text.split('\n'):
            pdf.multi_cell(0, 5, line)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{function_detail}", ln=True)

        pdf.add_page()
        pdf.cell(0, 10, "Original Input Bar Chart", ln=True)
        pdf.image(fig1_img_path, w=180)
        pdf.cell(0, 10, f"Total Original Value: {total_original}", ln=True)

        pdf.add_page()
        pdf.cell(0, 10, "Balanced Bar Chart", ln=True)
        pdf.image(fig2_img_path, w=180)
        pdf.cell(0, 10, f"Total Balanced Value: {total_balanced}", ln=True)

        pdf_path = os.path.join(tmpdir, f"{filename}-report.pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            return f.read()