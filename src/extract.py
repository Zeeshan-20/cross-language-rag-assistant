import json
import re
from pathlib import Path
import pymupdf

DATA_DIR = Path("data")


PAGE_RANGES = {}

# Tables that extraction cannot read correctly: written by hand from the PDF.
MANUAL_TABLES = {
    ("MaACS_SO_250318_de.pdf", 7): """Tabelle 1 (manuell aufbereitet): Regelstudienplan Master Applied Computer Science
Seminar: 5 CP im 3. Semester.
Projekt: 5 CP im 3. Semester.
Wahlpflichtbereich: 30 CP im 1. Semester, 30 CP im 2. Semester, 20 CP im 3. Semester.
Masterarbeit: 27 CP im 4. Semester.
Masterkolloquium: 3 CP im 4. Semester.
Summe Pflicht: 0 CP im 1. Semester, 0 CP im 2. Semester, 10 CP im 3. Semester, 30 CP im 4. Semester.
Summe pro Semester: 30 CP in jedem der 4 Semester.
Gesamt: 120 CP.""",
}


def clean(text):
    text = text.replace("ﬂ", "fl").replace("ﬁ", "fi").replace("ﬀ", "ff")  # ligatures
    text = re.sub(r"-\n(?=[a-zäöüß])", "", text)  # join words split at line end
    text = re.sub(r"[ \t]+", " ", text)           # collapse repeated spaces
    text = re.sub(r"\n\s*\n+", "\n", text)        # remove empty lines
    return text.strip()


def printed_page(text):
    """Page number printed in the footer, or None if not found."""
    m = re.search(r"SEITE\s+(\d+)", text)        # e.g. "SEITE 96" (Verkündungsblatt)
    if m:
        return int(m.group(1))
    last_line = text.strip().split("\n")[-1].strip()
    if last_line.isdigit():                       # e.g. "Nichtamtliche Lesefassung\n6"
        return int(last_line)
    return None


def extract_pdf(path):
    first, last = PAGE_RANGES.get(path.name, (1, None))
    pages = []
    with pymupdf.open(path) as doc:
        last = last or len(doc)
        for number in range(first, last + 1):
            text = clean(doc[number - 1].get_text())
            printed = printed_page(text)  # before adding manual text (footer must be last line)
            text += "\n" + MANUAL_TABLES.get((path.name, number), "")
            text = text.strip()
            if text:
                pages.append({
                    "source": path.name,
                    "page": number,
                    "printed_page": printed,
                    "text": text,
                })
    return pages


if __name__ == "__main__":
    all_pages = []
    for pdf in sorted(DATA_DIR.glob("*.pdf")):
        all_pages += extract_pdf(pdf)
    out = Path("data/pages.json")
    out.write_text(json.dumps(all_pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(all_pages)} pages")
    for p in all_pages:
        print(p["source"], "PDF", p["page"], "printed", p["printed_page"])