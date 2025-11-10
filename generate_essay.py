from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_LINE_SPACING

# IMPORTANT:
# - Do NOT change the content of ESSAY_TEXT yourself.
# - I will paste the full essay text between the triple quotes.
ESSAY_TEXT = """PUT_FULL_ESSAY_TEXT_HERE"""


def configure_document(doc: Document) -> None:
    """Configure global font, spacing, and margins."""
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_after = Pt(0)

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def main() -> None:
    """
    Create a Word document that contains EXACTLY the text in ESSAY_TEXT,
    line by line, with no extra content.

    - Each line in ESSAY_TEXT becomes one paragraph.
    - Empty lines become empty paragraphs (blank lines).
    """
    doc = Document()
    configure_document(doc)

    for line in ESSAY_TEXT.splitlines():
        p = doc.add_paragraph()
        run = p.add_run(line)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

    doc.save("Idiopathic_Short_Stature_Essay.docx")


if __name__ == "__main__":
    main()
