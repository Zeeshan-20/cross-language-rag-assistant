from pathlib import Path 
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

TITLES = {
    "Immatrikulationsordnung_HSM_vom_23.10.2019.pdf": "Immatrikulationsordnung(2019)",
    "MaACS_MD_250318_de.pdf": "Modulhandbuch(18.03.2025)",
    "MaACS_SO_250318_de.pdf": "Studienordnung(18.03.2025)",
    "Verkuendungsblatt_Nr._1_2025.pdf": "Prüfungsordnung(2025)",
}

pages = json.load(open("data/pages.json" , "r" , encoding="utf-8"))
#print(len(pages))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

chunks=[]
for p in pages:
    pieces = splitter.split_text(p["text"])
    for piece in pieces:
        chunk = {
            "id" : len(chunks),
            "title" : TITLES.get(p["source"], p["source"]),
            "source" : p["source"],
            "page" : p["page"],
            "printed_page": p["printed_page"] or 0,
            "text": piece,
        }
        chunks.append(chunk)
#print(chunks[0])
Path("data/chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(chunks), "chunks")
