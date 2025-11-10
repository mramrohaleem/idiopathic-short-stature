"""PowerPoint generator for the Idiopathic Short Stature essay.

Prerequisites:
    pip install python-pptx

Usage:
    Ensure ESSAY_TEXT contains the full essay, then run:
        python generate_ppt.py

The script builds a clean presentation with a title slide and one slide per
essay section, featuring structured bullet points and image placeholders.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


def parse_title_block(essay_text: str) -> Dict[str, Optional[str]]:
    """Extract title metadata from the first non-empty lines of the essay."""
    lines = [line.strip() for line in essay_text.splitlines() if line.strip()]
    title_data = {
        "title": lines[0] if len(lines) > 0 else "",
        "prepared_for": lines[1] if len(lines) > 1 else "",
        "student": lines[2] if len(lines) > 2 else "",
        "course": lines[3] if len(lines) > 3 else "",
        "date": lines[4] if len(lines) > 4 else "",
    }
    return title_data


def parse_sections(essay_text: str) -> List[Dict[str, str]]:
    """Return a list of numbered sections and their body text."""
    lines = essay_text.splitlines()
    sections: List[Dict[str, str]] = []
    current_heading: Optional[str] = None
    current_lines: List[str] = []

    def flush_current() -> None:
        if current_heading is None:
            return
        body = "\n".join(current_lines).strip()
        sections.append({"heading": current_heading, "body": body})

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(tuple(f"{n}. " for n in range(1, 10))):
            if current_heading is not None:
                flush_current()
                current_lines.clear()
            current_heading = stripped
        else:
            if current_heading is not None:
                current_lines.append(line)

    flush_current()
    return sections


def _split_into_paragraphs(body: str) -> List[str]:
    """Split section body into cleaned paragraphs separated by blank lines."""
    paragraphs: List[str] = []
    chunk: List[str] = []
    for line in body.splitlines():
        if line.strip():
            chunk.append(line.strip())
        else:
            if chunk:
                paragraphs.append(" ".join(chunk))
                chunk = []
    if chunk:
        paragraphs.append(" ".join(chunk))
    return paragraphs


def make_bullets_from_section(section_body: str) -> List[str]:
    """Create up to four short bullet strings from a section body."""
    bullets: List[str] = []
    for paragraph in _split_into_paragraphs(section_body):
        if "Reference:" in paragraph:
            continue
        sentence_end = paragraph.find(".")
        if sentence_end != -1:
            sentence = paragraph[: sentence_end + 1].strip()
        else:
            sentence = paragraph.strip()
        if not sentence:
            continue
        if len(sentence) > 150:
            sentence = sentence[:147].rstrip() + "..."
        bullets.append(sentence)
        if len(bullets) == 4:
            break
    return bullets


def _add_title_bar(slide, heading: str) -> None:
    """Add a colored title bar with centered heading text."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1)
    )
    fill = bar.fill
    fill.solid()
    try:
        bar.fill.fore_color.rgb = 0x4F81BD
    except AttributeError:
        pass
    bar.line.width = Pt(0)
    text_frame = bar.text_frame
    text_frame.clear()
    paragraph = text_frame.paragraphs[0]
    paragraph.text = heading
    paragraph.font.name = "Calibri"
    paragraph.font.size = Pt(34)
    paragraph.font.bold = True
    try:
        paragraph.font.color.rgb = 0xFFFFFF
    except AttributeError:
        pass
    paragraph.alignment = PP_ALIGN.CENTER
    text_frame.margin_bottom = 0
    text_frame.margin_top = 0


def _add_bullet_box(slide, bullets: List[str]) -> None:
    """Add a left-column text box populated with bullet points."""
    textbox = slide.shapes.add_textbox(
        Inches(0.5), Inches(1.3), Inches(6.0), Inches(4.5)
    )
    text_frame = textbox.text_frame
    text_frame.clear()
    text_frame.word_wrap = True
    text_frame.margin_left = Inches(0.1)
    text_frame.margin_right = Inches(0.1)

    if not bullets:
        paragraph = text_frame.paragraphs[0]
        paragraph.text = "Key points forthcoming"
        paragraph.font.name = "Calibri"
        paragraph.font.size = Pt(22)
        paragraph.alignment = PP_ALIGN.LEFT
        return

    for index, bullet in enumerate(bullets):
        paragraph = text_frame.paragraphs[0] if index == 0 else text_frame.add_paragraph()
        paragraph.text = bullet
        paragraph.level = 0
        paragraph.font.name = "Calibri"
        paragraph.font.size = Pt(22)
        paragraph.line_spacing = 1.15
        paragraph.alignment = PP_ALIGN.LEFT


def _suggested_image_text(heading: str) -> str:
    """Return context-specific suggested image text based on section heading."""
    mapping = {
        "1.": "Suggested image:\nChild growth chart / clinic overview",
        "2.": "Suggested image:\nGrowth plate / GH-IGF-1 axis diagram",
        "3.": "Suggested image:\nDNA / gene mutation illustration",
        "4.": "Suggested image:\nGrowth chart, lab tests, X-ray",
        "5.": "Suggested image:\nChildren interacting / school setting",
        "6.": "Suggested image:\nGH injection / medication",
        "7.": "Suggested image:\nScales / healthcare costs",
        "8.": "Suggested image:\nLab research / future medicine",
        "9.": "Suggested image:\nHealthy adolescent / family",
    }
    for prefix, text in mapping.items():
        if heading.startswith(prefix):
            return text
    return "Suggested image:\nRelevant clinical visual"


def _add_image_placeholder(slide, heading: str) -> None:
    """Add a right-column rectangle acting as an image placeholder."""
    placeholder = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.3), Inches(3.0), Inches(4.0)
    )
    placeholder.fill.solid()
    try:
        placeholder.fill.fore_color.rgb = 0xF2F2F2
        placeholder.line.color.rgb = 0x999999
    except AttributeError:
        pass
    placeholder.line.width = Pt(1)
    text_frame = placeholder.text_frame
    text_frame.clear()
    text_frame.vertical_anchor = 1  # Equivalent to MSO_ANCHOR.MIDDLE
    paragraph = text_frame.paragraphs[0]
    paragraph.text = _suggested_image_text(heading)
    paragraph.font.name = "Calibri"
    paragraph.font.size = Pt(14)
    paragraph.alignment = PP_ALIGN.CENTER


def _build_title_slide(prs: Presentation, title_data: Dict[str, Optional[str]]) -> None:
    """Create the title slide using the parsed metadata."""
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_shape = slide.shapes.title
    subtitle_shape = slide.placeholders[1]

    title_shape.text = title_data.get("title") or ""
    title_paragraph = title_shape.text_frame.paragraphs[0]
    title_paragraph.font.name = "Calibri"
    title_paragraph.font.size = Pt(38)
    title_paragraph.font.bold = True
    title_paragraph.alignment = PP_ALIGN.CENTER

    subtitle_lines = [
        title_data.get("prepared_for") or "",
        title_data.get("student") or "",
        title_data.get("course") or "",
    ]
    subtitle_shape.text = "\n".join(line for line in subtitle_lines if line)
    for paragraph in subtitle_shape.text_frame.paragraphs:
        paragraph.font.name = "Calibri"
        paragraph.font.size = Pt(22)
        paragraph.alignment = PP_ALIGN.CENTER

    date_text = title_data.get("date") or ""
    if date_text:
        date_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.5), Inches(9.0), Inches(0.4)
        )
        frame = date_box.text_frame
        frame.text = date_text
        paragraph = frame.paragraphs[0]
        paragraph.font.name = "Calibri"
        paragraph.font.size = Pt(14)
        paragraph.alignment = PP_ALIGN.RIGHT


def _build_section_slide(prs: Presentation, section: Dict[str, str]) -> None:
    """Create a slide for a single essay section."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    heading = section["heading"]
    bullets = make_bullets_from_section(section["body"])

    _add_title_bar(slide, heading)
    _add_bullet_box(slide, bullets)
    _add_image_placeholder(slide, heading)


def build_presentation_from_essay(essay_text: str) -> Presentation:
    """Parse essay text and build a professional PowerPoint presentation."""
    presentation = Presentation()
    title_data = parse_title_block(essay_text)
    sections = parse_sections(essay_text)

    _build_title_slide(presentation, title_data)
    for section in sections:
        _build_section_slide(presentation, section)

    return presentation


def main() -> None:
    try:
        essay_text = globals()["ESSAY_TEXT"]
    except KeyError as exc:  # pragma: no cover - runtime safeguard
        raise RuntimeError(
            "ESSAY_TEXT must be defined at the top of generate_ppt.py before running."
        ) from exc
    presentation = build_presentation_from_essay(essay_text)
    presentation.save("Idiopathic_Short_Stature_Presentation.pptx")


if __name__ == "__main__":
    main()
