import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re

TITLES = {
    "Immatrikulationsordnung_HSM_vom_23.10.2019.pdf": "Immatrikulationsordnung(2019)",
    "MaACS_MD_250318_de.pdf": "Modulhandbuch(18.03.2025)",
    "MaACS_SO_250318_de.pdf": "Studienordnung(18.03.2025)",
    "Verkuendungsblatt_Nr._1_2025.pdf": "Prüfungsordnung(2025)",
}

def make_chunks():
    pages = json.load(open("data/pages.json", encoding="utf-8"))

    documents = []
    current_module = ""
    for p in pages:
        if p["source"].startswith("MaACS_MD"):
            m = re.search(r"Modulname\s*\n(.+)", p["text"])
            if m:
                current_module = m.group(1).strip()
            module = current_module
        else:
            module = ""

        documents.append(Document(
            page_content=p["text"],
            metadata={
                "title": TITLES.get(p["source"], p["source"]),
                "source": p["source"],
                "page": p["page"],
                "printed_page": p["printed_page"] or 0,
                "module": module,
            },
        ))
    #print(documents[0])
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    # print(len(chunks), "chunks")
    for c in chunks:
        if c.metadata["module"]:
            c.page_content = f"Modul: {c.metadata['module']}\n{c.page_content}"
    return chunks