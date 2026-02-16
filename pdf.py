from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile
import os
from datetime import datetime


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbers and headers/footers"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        page = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 0.75*inch, 0.5*inch, page)
        
        # Footer text
        self.drawString(0.75*inch, 0.5*inch, f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")


# Vastu directional color scheme matching Streamlit app
VASTU_COLORS = [
    "#2986FF",  # NNW - Blue
    "#2986FF",  # NORTH - Blue
    "#2986FF",  # NNE - Blue
    "#2986FF",  # NE - Blue
    "#24FF53",  # ENE - Green
    "#24FF53",  # EAST - Green
    "#24FF53",  # ESE - Green
    "#FF3232",  # SE - Red
    "#FF3232",  # SSE - Red
    "#FF3232",  # SOUTH - Red
    "#fbff1f",  # SSW - Yellow
    "#fbff1f",  # SW - Yellow
    "#b4b4b4",  # WSW - Gray
    "#b4b4b4",  # WEST - Gray
    "#b4b4b4",  # WNW - Gray
    "#b4b4b4",  # NW - Gray
]

DIRECTION_LABELS = ["NNW","NORTH","NNE","NE","ENE","EAST","ESE","SE","SSE","SOUTH","SSW","SW","WSW","WEST","WNW","NW"]


def _safe_write_plotly_png(fig, path_png, fallback_labels=None, fallback_values=None):
    """
    Try saving a Plotly fig to PNG using Kaleido (Chrome required).
    If that fails, fall back to a styled Matplotlib bar chart with Vastu colors.
    """
    try:
        import kaleido
        chrome_path = os.environ.get("KaleidoExecutablePath")
        if not chrome_path:
            try:
                chrome_path = str(kaleido.get_chrome_sync())
                os.environ["KaleidoExecutablePath"] = chrome_path
            except Exception as e:
                print("⚠️ Kaleido portable Chrome fetch failed:", e)
        fig.write_image(path_png, format="png", engine="kaleido", width=1400, height=700)
        return
    except Exception as e:
        print("❌ Kaleido export failed:", e)
        print("➡️ Falling back to Matplotlib static render...")

    # Fallback with styled matplotlib using Vastu colors
    import matplotlib.pyplot as plt
    if fallback_labels is None or fallback_values is None:
        plt.figure(figsize=(12, 6))
        plt.text(0.5, 0.5, "Chart unavailable", ha='center', va='center', fontsize=16)
        plt.axis('off')
        plt.savefig(path_png, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return

    # Create matplotlib fallback with Vastu color scheme
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='white')
    
    # Use Vastu colors for bars
    bar_colors = VASTU_COLORS[:len(fallback_labels)]
    
    bars = ax.bar(fallback_labels, fallback_values, color=bar_colors, edgecolor='white', linewidth=2, width=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Calculate reference lines
    avg = sum(fallback_values) / len(fallback_values)
    max_line = (max(fallback_values) + avg) / 2
    min_line = (min(fallback_values) + avg) / 2
    
    # Add reference lines
    ax.axhline(y=avg, color='blue', linestyle='--', linewidth=2, label='Avg Area', alpha=0.7)
    ax.axhline(y=max_line, color='green', linestyle=':', linewidth=2, label='Max Line', alpha=0.7)
    ax.axhline(y=min_line, color='red', linestyle=':', linewidth=2, label='Min Line', alpha=0.7)
    
    ax.set_xlabel('Zones', fontsize=13, fontweight='bold')
    ax.set_ylabel('Area', fontsize=13, fontweight='bold')
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(ha='right')
    plt.tight_layout()
    plt.savefig(path_png, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def get_direction_color_hex(label):
    """Get the hex color for a direction label"""
    try:
        idx = DIRECTION_LABELS.index(label)
        return VASTU_COLORS[idx]
    except (ValueError, IndexError):
        return "#b4b4b4"  # Default gray


def hex_to_reportlab_color(hex_color):
    """Convert hex color to ReportLab color object"""
    return colors.HexColor(hex_color)


def generate_pdf(
    df,
    fig1,
    fig2,
    filename,
    total_original,
    total_balanced,
    function_detail,
    orig_values=None,
    bal_values=None,
    labels=None
):
    """Generate a professional-looking PDF report with Vastu color scheme"""
    
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

        # Save chart images
        _safe_write_plotly_png(fig1, fig1_path, fallback_labels=labels, fallback_values=orig_values)
        _safe_write_plotly_png(fig2, fig2_path, fallback_labels=labels, fallback_values=bal_values)

        # Create PDF with custom canvas for page numbers
        pdf_path = os.path.join(tmpdir, f"{filename}-report.pdf")
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['BodyText'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            leading=16
        )

        # Title
        elements.append(Paragraph(f"Vastu Bar Chart Balancing Report", title_style))
        elements.append(Paragraph(f"Project: {filename}", subtitle_style))
        elements.append(Spacer(1, 0.2*inch))

        # Summary Metrics Cards
        elements.append(Paragraph("Executive Summary", heading_style))
        
        # Calculate metrics
        original_sum = sum(orig_values) if orig_values else 0
        balanced_sum = sum(bal_values) if bal_values else 0
        original_avg = original_sum / len(orig_values) if orig_values else 0
        balanced_avg = balanced_sum / len(bal_values) if bal_values else 0
        original_std = (sum((x - original_avg) ** 2 for x in orig_values) / len(orig_values)) ** 0.5 if orig_values else 0
        balanced_std = (sum((x - balanced_avg) ** 2 for x in bal_values) / len(bal_values)) ** 0.5 if bal_values else 0
        
        # Metrics table with color-coded header
        metrics_data = [
            ['Metric', 'Original', 'Balanced', 'Change'],
            ['Total Area', f'{original_sum:.2f}', f'{balanced_sum:.2f}', f'{balanced_sum - original_sum:+.2f}'],
            ['Average Area', f'{original_avg:.2f}', f'{balanced_avg:.2f}', f'{balanced_avg - original_avg:+.2f}'],
            ['Std Deviation', f'{original_std:.2f}', f'{balanced_std:.2f}', f'{balanced_std - original_std:+.2f}'],
            ['Min Value', f'{min(orig_values):.2f}' if orig_values else 'N/A', 
             f'{min(bal_values):.2f}' if bal_values else 'N/A', ''],
            ['Max Value', f'{max(orig_values):.2f}' if orig_values else 'N/A', 
             f'{max(bal_values):.2f}' if bal_values else 'N/A', '']
        ]

        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2986FF')),  # Blue header like North direction
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))

        # Algorithm Details
        elements.append(Paragraph("Algorithm Configuration", heading_style))
        elements.append(Paragraph(function_detail, body_style))
        elements.append(Spacer(1, 0.2*inch))

        # Data Table with color-coded rows matching Vastu directions
        elements.append(Paragraph("Detailed Zone Comparison", heading_style))
        
        # Prepare table data with colors
        table_data = [['Zone', 'Direction', 'Original Value', 'Balanced Value', 'Difference']]
        table_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#24FF53')),  # Green header like East direction
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        for idx, row in df.iterrows():
            if "Zone" in df.columns:
                label = row["Zone"]
            elif "Label" in df.columns:
                label = row["Label"]
            else:
                label = f"Item {idx+1}"
            
            if "Original Value" in df.columns:
                orig = row["Original Value"]
            elif "Value" in df.columns:
                orig = row["Value"]
            else:
                orig = orig_values[idx] if orig_values else 0
            
            if "Balanced Value" in df.columns:
                bal = row["Balanced Value"]
            else:
                bal = bal_values[idx] if bal_values else 0
            
            diff = bal - orig
            
            # Get color for this direction
            direction_color = get_direction_color_hex(label)
            
            table_data.append([
                str(idx + 1),
                str(label),
                f'{orig:.2f}',
                f'{bal:.2f}',
                f'{diff:+.2f}'
            ])
            
            # Add background color for this row matching the direction
            row_num = idx + 1
            table_styles.append(('BACKGROUND', (0, row_num), (-1, row_num), hex_to_reportlab_color(direction_color)))
            
            # Adjust text color based on background brightness
            if direction_color in ['#fbff1f', '#24FF53', '#b4b4b4']:  # Yellow, Green, Gray - use dark text
                table_styles.append(('TEXTCOLOR', (0, row_num), (-1, row_num), colors.black))
            else:  # Blue and Red - use white text
                table_styles.append(('TEXTCOLOR', (0, row_num), (-1, row_num), colors.white))

        data_table = Table(table_data, colWidths=[0.6*inch, 1.4*inch, 1.6*inch, 1.6*inch, 1.3*inch])
        data_table.setStyle(TableStyle(table_styles))
        elements.append(data_table)

        # Add color legend
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Zone Color Legend", heading_style))
        
        legend_data = [
            ['Color', 'Directions', 'Element'],
            ['', 'NNW, NORTH, NNE, NE', 'Water (North)'],
            ['', 'ENE, EAST, ESE', 'Wood (East)'],
            ['', 'SE, SSE, SOUTH', 'Fire (South)'],
            ['', 'SSW, SW', 'Earth (Southwest)'],
            ['', 'WSW, WEST, WNW, NW', 'Metal (West)']
        ]
        
        legend_table = Table(legend_data, colWidths=[0.8*inch, 3*inch, 2.7*inch])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#2986FF')),  # Blue
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#24FF53')),  # Green
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#FF3232')),  # Red
            ('BACKGROUND', (0, 4), (0, 4), colors.HexColor('#fbff1f')),  # Yellow
            ('BACKGROUND', (0, 5), (0, 5), colors.HexColor('#b4b4b4')),  # Gray
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(legend_table)

        # Page break before charts
        elements.append(PageBreak())

        # Original Chart
        elements.append(Paragraph("Original Input Bar Chart", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        if os.path.exists(fig1_path):
            img1 = Image(fig1_path, width=6.5*inch, height=3.25*inch)
            elements.append(img1)
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(total_original, body_style))
        
        # Page break before balanced chart
        elements.append(PageBreak())

        # Balanced Chart
        elements.append(Paragraph("Balanced Bar Chart", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        if os.path.exists(fig2_path):
            img2 = Image(fig2_path, width=6.5*inch, height=3.25*inch)
            elements.append(img2)
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(total_balanced, body_style))

        # Add conclusion section
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Vastu Analysis Conclusion", heading_style))
        
        variance_reduction = ((original_std - balanced_std) / original_std * 100) if original_std > 0 else 0
        conclusion_text = f"""
        The Vastu balancing algorithm successfully reduced the standard deviation by {variance_reduction:.1f}%, 
        resulting in a more harmonious distribution of energy across all directional zones. The total area 
        changed from {original_sum:.2f} to {balanced_sum:.2f}, representing a {((balanced_sum - original_sum) / original_sum * 100) if original_sum != 0 else 0:.2f}% change.
        This balanced configuration promotes better energy flow according to Vastu principles, with each 
        directional zone (North-Water, East-Wood, South-Fire, Southwest-Earth, West-Metal) approaching 
        optimal proportions.
        """
        elements.append(Paragraph(conclusion_text, body_style))

        # Build PDF with custom canvas
        doc.build(elements, canvasmaker=NumberedCanvas)

        with open(pdf_path, "rb") as f:
            return f.read()
