"""
PDF Generator for Twitter Data Mining & NLP Intelligence Suite
Creates a professionally styled, publication-ready PDF documentation & presentation cue sheet.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas for adding page numbers and running footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Twitter / X Data Mining & NLP Intelligence Suite — Technical Defense Guide")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential & Proprietary — Author: omprajapatirk-source")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf(filename="Twitter_Data_Mining_NLP_Suite_Guide.pdf"):
    pdf_path = Path(filename).resolve()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette
    PRIMARY = colors.HexColor("#4f46e5")    # Indigo
    SECONDARY = colors.HexColor("#0284c7")  # Ocean Blue
    DARK_TEXT = colors.HexColor("#0f172a")  # Slate 900
    BODY_TEXT = colors.HexColor("#334155")  # Slate 700
    MUTED_TEXT = colors.HexColor("#64748b") # Slate 500
    BG_LIGHT = colors.HexColor("#f8fafc")   # Slate 50
    BORDER_COLOR = colors.HexColor("#cbd5e1") # Slate 300

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=MUTED_TEXT,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=BODY_TEXT,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
        backColor=BG_LIGHT,
        borderPadding=4,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#1e1b4b"),
        backColor=colors.HexColor("#eef2ff"),
        borderColor=PRIMARY,
        borderWidth=1,
        borderPadding=6,
        spaceAfter=6,
        spaceBefore=4
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("Twitter / X Data Mining &amp; NLP Intelligence Suite", title_style))
    story.append(Paragraph("<b>Author:</b> omprajapatirk-source &bull; <b>Architecture:</b> Marco Bonzanini Social NLP Framework &bull; <b>Stack:</b> Python 3, Flask, Chart.js, Vis.js, Leaflet", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary &amp; Problem Statement", h1_style))
    story.append(Paragraph(
        "Social media text represents one of the most volatile, unstructured forms of human communication. Standard NLP tokenizers often fail on tweets because they split on non-alphanumeric punctuation, destroying entities such as <code>@mentions</code>, <code>#hashtags</code>, URLs, and ASCII emoticons (e.g., <code>:)</code>, <code>:D</code>). This project implements an end-to-end 5-stage NLP pipeline that captures, normalizes, statistically analyzes, and visualizes social media data in real time.",
        body_style
    ))

    # 2. Pipeline Summary Table
    story.append(Paragraph("2. 5-Stage NLP Pipeline Architecture", h1_style))
    
    table_data = [
        [
            Paragraph("<b>Stage</b>", h2_style),
            Paragraph("<b>Module File</b>", h2_style),
            Paragraph("<b>Core Mathematical / Technical Functionality</b>", h2_style)
        ],
        [
            Paragraph("<b>1. Ingestion</b>", body_style),
            Paragraph("<code>src/collector.py</code><br/><code>src/mock_generator.py</code>", code_style),
            Paragraph("Twitter API v2 (<code>tweepy.Client</code>) search queries or 10-city global geotagged simulation generator. Includes in-memory &amp; <code>/tmp</code> storage fallback for serverless hosting.", body_style)
        ],
        [
            Paragraph("<b>2. Tokenization</b>", body_style),
            Paragraph("<code>src/tokenizer.py</code>", code_style),
            Paragraph("9-component custom regex preserving Twitter handles, hashtags, emoticons, Unicode emojis (🚀, 🔥), and URLs. Strips 150+ English stopwords and social noise (<code>rt</code>, <code>via</code>, <code>amp</code>).", body_style)
        ],
        [
            Paragraph("<b>3. Stat Mining</b>", body_style),
            Paragraph("<code>src/analyzer.py</code>", code_style),
            Paragraph("Unigrams, Bigrams, symmetric <i>N &times; N</i> Co-occurrence Matrix, and <b>Pointwise Mutual Information (PMI)</b> computation for semantic affinity.", body_style)
        ],
        [
            Paragraph("<b>4. Sentiment</b>", body_style),
            Paragraph("<code>src/sentiment.py</code>", code_style),
            Paragraph("Normalized polarity scoring (-1.0 to +1.0) with 3-word negation context windows, intensifier multipliers, emoticon weighting, and multi-class topic clustering.", body_style)
        ],
        [
            Paragraph("<b>5. Visual Suite</b>", body_style),
            Paragraph("<code>server.py</code><br/><code>static/app.js</code>", code_style),
            Paragraph("Flask REST API + Glassmorphism UI integrating Chart.js bar/doughnut charts, Vis.js Barnes-Hut physics network graph, and Leaflet CartoDB world maps.", body_style)
        ]
    ]

    t = Table(table_data, colWidths=[1.1*inch, 1.4*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    # 3. Mathematical Formulations
    story.append(Paragraph("3. Core Mathematical &amp; Algorithmic Formulations", h1_style))
    
    story.append(Paragraph("<b>A. Pointwise Mutual Information (PMI):</b>", h2_style))
    story.append(Paragraph(
        "Quantifies whether term <i>X</i> and term <i>Y</i> co-occur due to true semantic affinity or random corpus distribution:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>PMI(x, y) = log<sub>2</sub> [ P(x, y) / (P(x) &bull; P(y)) ]</b><br/>"
        "Where <i>P(x)</i> = Count(x) / N, <i>P(y)</i> = Count(y) / N, and <i>P(x,y)</i> = Co-occurrence(x, y) / N.",
        body_style
    ))

    story.append(Paragraph("<b>B. Laplace-Smoothed Sentiment Polarity Formula:</b>", h2_style))
    story.append(Paragraph(
        "Evaluates weighted positive signals (<i>S<sub>pos</sub></i>) and negative signals (<i>S<sub>neg</sub></i>):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Polarity Score = (S<sub>pos</sub> - S<sub>neg</sub>) / [ (S<sub>pos</sub> + S<sub>neg</sub>) + 1.0 ]</b><br/>"
        "Bounded strictly in [-1.0, +1.0]. Negation words (<i>not, never, don't</i>) invert the valence of the subsequent 3 tokens.",
        body_style
    ))

    # 4. Spoken Presentation Cue Sheet
    story.append(Spacer(1, 4))
    story.append(Paragraph("4. Presentation Teleprompter / Read-Along Script", h1_style))
    story.append(Paragraph(
        "<b>[0:00 - 0:30] Introduction:</b> \"Hello! Today, I am presenting my Twitter Data Mining &amp; NLP Intelligence Suite — an end-to-end Python platform inspired by Marco Bonzanini's data science framework, modernized for Twitter API v2 and cloud deployment.\"",
        callout_style
    ))
    story.append(Paragraph(
        "<b>[0:30 - 1:15] NLP Tokenizer:</b> \"Social media text is uniquely unstructured. Standard NLP tokenizers break on @handles, #hashtags, and emoticons. Our 9-component custom regex isolates entities, extracts emoticons, and strips stopwords and Twitter noise (rt, via, https).\"",
        callout_style
    ))
    story.append(Paragraph(
        "<b>[1:15 - 2:00] Frequencies &amp; Co-occurrence Graph:</b> \"Next, the engine calculates unigrams, bigrams, and builds a symmetric N&times;N co-occurrence matrix. Our interactive Vis.js physics graph clusters related terms, while Pointwise Mutual Information (PMI) mathematically measures true word associations.\"",
        callout_style
    ))
    story.append(Paragraph(
        "<b>[2:00 - 2:45] Sentiment, Map &amp; Conclusion:</b> \"Our context-aware sentiment analyzer scores polarity from -1.0 to +1.0 using negation windows, and plots geotagged tweets live on an interactive Leaflet world map. The app is open-source on GitHub and deployed on Vercel. Thank you!\"",
        callout_style
    ))

    # Build PDF with Page Numbers
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully built PDF at: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    build_pdf()
