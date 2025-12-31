
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Add project root to path if needed
sys.path.append(str(Path(__file__).parent.parent))

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors
except ImportError:
    print("Error: reportlab not installed. Please run 'pip install reportlab'")
    sys.exit(1)

def clean_text(text):
    """Convert basic markdown to reportlab-compatible HTML tags."""
    # Replace **text** with <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Replace *text* with <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text

def convert_md_to_pdf(md_path, pdf_path):
    print(f"Converting {md_path} to {pdf_path}...")
    
    with open(md_path, 'r') as f:
        lines = f.readlines()
        
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#1a237e')
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.HexColor('#455a64'),
        fontName='Helvetica-Bold'
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#0d47a1')
    )
    
    body_style = styles['Normal']
    body_style.fontSize = 11
    body_style.leading = 14
    
    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        leftIndent=20,
        rightIndent=20,
        fontName='Helvetica-Oblique',
        backColor=colors.HexColor('#f5f5f5'),
        borderPadding=10,
        spaceBefore=10,
        spaceAfter=10
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=24
    )

    elements = []
    
    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 12))
            continue
            
        # Title (# )
        if line.startswith('# '):
            elements.append(Paragraph(line[2:], title_style))
        # Bold Subtitle (** )
        elif line.startswith('**') and line.endswith('**'):
            elements.append(Paragraph(line[2:-2], subtitle_style))
        # H2 (## )
        elif line.startswith('## '):
            elements.append(Paragraph(line[3:], h2_style))
        # Horizontal Rule (---)
        elif line == '---':
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=6, spaceAfter=6))
        # Quote (> )
        elif line.startswith('> '):
            elements.append(Paragraph(clean_text(line[2:]), quote_style))
        # Bullet Points (- or * or 1.)
        elif line.startswith('- ') or line.startswith('* ') or (line[0:1].isdigit() and (line[1:3] == '. ' or line[2:4] == '. ')):
            elements.append(Paragraph(clean_text(line), body_style))
        # Footer (italic with copyright)
        elif line.startswith('*©'):
            elements.append(Paragraph(line.replace('*', ''), footer_style))
        else:
            elements.append(Paragraph(clean_text(line), body_style))
            
    doc.build(elements)
    print(f"Success: {pdf_path} created.")

def main():
    bonus_dir = Path("/home/adminmatej/github/brain-2026/academy/bonus")
    output_dir = Path("/home/adminmatej/github/applications/focus-kraliki/static/academy")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for md_file in bonus_dir.glob("*.md"):
        pdf_file = output_dir / f"{md_file.stem}.pdf"
        convert_md_to_pdf(md_file, pdf_file)

if __name__ == "__main__":
    main()
