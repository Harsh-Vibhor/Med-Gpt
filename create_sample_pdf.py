"""
Create a sample medical PDF for testing the RAG pipeline
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Create PDF
pdf_path = "data/docs/diabetes_guide.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor='black',
    spaceAfter=30,
    alignment=TA_CENTER
)
heading_style = styles['Heading2']
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    alignment=TA_JUSTIFY,
    spaceAfter=12
)

# Add content
elements.append(Paragraph("Understanding Diabetes", title_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("What is Diabetes", heading_style))
elements.append(Paragraph(
    "A chronic metabolic condition characterized by elevated blood glucose (hyperglycemia). "
    "It results from the pancreas not producing enough insulin (the hormone regulating blood sugar) "
    "or the body's cells becoming resistant to insulin's effects, or both.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Types of Diabetes", heading_style))
elements.append(Paragraph(
    "<b>Type 1 (Autoimmune):</b> An autoimmune condition where the immune system destroys "
    "insulin-producing beta cells in the pancreas, leading to absolute insulin deficiency. "
    "Requires lifelong insulin therapy.",
    body_style
))
elements.append(Paragraph(
    "<b>Type 2 (Insulin Resistance):</b> Primarily involves insulin resistance, where cells fail "
    "to respond properly to insulin, combined with progressive pancreatic beta-cell dysfunction. "
    "Often managed with lifestyle changes and oral medications.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Common Symptoms", heading_style))
elements.append(Paragraph(
    "• Polyuria (frequent urination)<br/>"
    "• Polydipsia (excessive thirst)<br/>"
    "• Polyphagia (extreme hunger)<br/>"
    "• Unexplained weight loss (more common in Type 1)<br/>"
    "• Fatigue and blurred vision",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Risk Factors", heading_style))
elements.append(Paragraph(
    "<b>Type 1:</b> Genetic predisposition, viral triggers, early-life factors.<br/>"
    "<b>Type 2:</b> Obesity/overweight, physical inactivity, poor diet (high processed fats/sugar), "
    "increasing age, family history, certain ethnicities, gestational diabetes history.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Management and Treatment", heading_style))
elements.append(Paragraph(
    "Focuses on achieving and maintaining target blood glucose levels to prevent complications. "
    "Key components include:<br/>"
    "• <b>Monitoring:</b> Regular blood glucose monitoring (SMBG or CGM).<br/>"
    "• <b>Lifestyle:</b> Balanced diet (carbohydrate counting), regular physical activity, weight management.<br/>"
    "• <b>Medications:</b> Insulin therapy (exogenous insulin) for Type 1 (and some Type 2). "
    "Oral antidiabetic agents (e.g., metformin) and injectables (e.g., GLP-1 RAs) for Type 2.",
    body_style
))

# Build PDF
doc.build(elements)
print(f"Sample PDF created: {pdf_path}")
