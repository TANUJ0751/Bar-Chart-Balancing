from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import imgkit
import os

def _safe_write_plotly_png(fig, path_png, fallback_labels=None, fallback_values=None):
    """
    Try saving a Plotly fig to PNG using Kaleido (Chrome required).
    If that fails, fall back to a basic Matplotlib bar chart using provided data.
    """
    try:
        import kaleido
        chrome_path = os.environ.get("KaleidoExecutablePath")
        if not chrome_path:
            try:
                chrome_path = str(kaleido.get_chrome_sync())  # ✅ FIX: convert Path to str
                os.environ["KaleidoExecutablePath"] = chrome_path
            except Exception as e:
                print("⚠️ Kaleido portable Chrome fetch failed:", e)
        fig.write_image(path_png, format="png", engine="kaleido")
        return
    except Exception as e:
        print("❌ Kaleido export failed:", e)
        print("➡️ Falling back to Matplotlib static render...")

    # ---- Fallback ----
    import matplotlib.pyplot as plt
    if fallback_labels is None or fallback_values is None:
        plt.figure(figsize=(6, 2))
        plt.text(0.5, 0.5, "Chart unavailable", ha='center', va='center')
        plt.axis('off')
        plt.savefig(path_png, dpi=120, bbox_inches='tight')
        plt.close()
        return

    plt.figure(figsize=(10, 4))
    plt.bar(fallback_labels, fallback_values)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path_png, dpi=150)
    plt.close()


def generate_pdf(
    df,
    fig1,
    fig2,
    filename,
    total_original,
    total_balanced,
    function_detail,
    orig_values=None,       # list of original numeric values (optional; used for fallback)
    bal_values=None,        # list of balanced numeric values (optional; used for fallback)
    labels=None             # list of labels (optional; fallback)
):
    # Default fallback data from df if not provided
    if labels is None and "Zone" in df.columns:
        labels = df["Zone"].tolist()
    elif labels is None and "Label" in df.columns:
        labels = df["Label"].tolist()

    if orig_values is None:
        if "Original Value" in df.columns:
            orig_values = df["Original Value"].tolist()
        elif "Value" in df.columns:
            orig_values = df["Value"].tolist()

    if bal_values is None:
        if "Balanced Value" in df.columns:
            bal_values = df["Balanced Value"].tolist()

    with tempfile.TemporaryDirectory() as tmpdir:
        fig1_path = os.path.join(tmpdir, "original_chart.png")
        fig2_path = os.path.join(tmpdir, "balanced_chart.png")

        # Save plotly OR fallback chart images
        # _safe_write_plotly_png(fig1, fig1_path, fallback_labels=labels, fallback_values=orig_values)
        # _safe_write_plotly_png(fig2, fig2_path, fallback_labels=labels, fallback_values=bal_values)

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

        # Function details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{function_detail}", ln=True)

        # Original Chart Page
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Original Input Bar Chart", ln=True)
        fig1.write_image(fig1_path, format="png", engine="kaleido", scale=2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Total Original Value: {total_original}", ln=True)

        # Balanced Chart Page
        pdf.add_page()
        pdf.ln(10)
        pdf.cell(0, 10, "Balanced Bar Chart", ln=True)
        fig2.write_image(fig1_path, format="png", engine="kaleido", scale=2)

        # Summary
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