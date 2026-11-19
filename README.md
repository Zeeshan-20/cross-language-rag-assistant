# cross-language-rag-assistant
Ask questions in English, get answers from German university regulations. The assistant quotes the original German text and cites the document and page.

Unofficial student project, not legal advice. For anything binding, check the official documents.

<img width="800" alt="Screenshot of the Gradio app" src="https://github.com/user-attachments/assets/5b82d53c-6b28-4c2e-84a0-fbff9b10acf2" />

## Example

Question: In which semester is the seminar and how many credit points does it have?

Answer: The seminar is in the 3rd semester and has 5 credit points (CP). "Seminar: 5 CP im 3. Semester." (Studienordnung, page 6).

Question: How many students are enrolled at Hochschule Schmalkalden?

Answer: I could not find this in the documents.

If the documents do not contain the answer, the assistant says: "I could not find this in the documents."

```
PDFs (German) -> extract -> chunk -> embed -> Chroma
                                              |
English question -> search (15 chunks) -> LLM re-ranking (best 6) -> LLM answer in English + German quote + page
```

| Step | File | What it does |
|---|---|---|
| 1. Extract | `src/extract.py` | Reads the PDFs with PyMuPDF and cleans the German text (ligatures, split words). Keeps the printed page numbers and adds one hand-transcribed table. Writes `data/pages.json`. |
| 2. Chunk | `src/chunk.py` | Splits pages into chunks (1000 characters, 200 overlap) that keep their title and page. Every Modulhandbuch chunk starts with its module name, so a chunk never loses track of which module it belongs to. |
| 3. Index | `src/index.py` | Embeds the chunks with OpenAI `text-embedding-3-small` and stores them in a local Chroma database. |
| 4. Retrieve | `src/retrieve.py` | Finds the 15 closest chunks. An LLM re-ranks them and the best 6 are kept. |
| 5. Answer | `src/answer.py` | Answers only from the retrieved German text, quotes it, cites the source, and says "not found" if the answer is missing. Follow-up questions use the chat history. |
| 6. App | `src/app.py` | Gradio chat interface. |
| Eval | `eval/` | Test questions and a script that measures retrieval quality. |

## Documents used

The PDFs are not in this repository. Download them and put them in the `data/` folder:

| Document | Date | Download |
|---|---|---|
| Studienordnung Master Applied Computer Science | 18.03.2025 | https://drive.google.com/file/d/1d1rHyM3ByAfmX32Sf_PgbuWz5XQoZ8QC/view?usp=sharing |
| Modulhandbuch Master Applied Computer Science | 18.03.2025 | https://drive.google.com/file/d/15z3KCBqsAbDfWEMAF8-BXVshVP5T0dcl/view?usp=sharing |
| Prüfungsordnung (Verkündungsblatt Nr. 1/2025) | 2025 | https://drive.google.com/file/d/1xFx3CQAw-4hJKk9MYAXi-wv2ynpk778D/view?usp=sharing |
| Immatrikulationsordnung (Verkündungsblatt Nr. 7/2019) | 23.10.2019 | https://drive.google.com/file/d/186GBAWUTJdtgVa-zOY3HW-Oy-y9w3ZhE/view?usp=sharing |

The code expects these file names: `MaACS_SO_250318_de.pdf`, `MaACS_MD_250318_de.pdf`, `Verkuendungsblatt_Nr._1_2025.pdf`, `Immatrikulationsordnung_HSM_vom_23.10.2019.pdf`.

## Setup

You need Python 3.12 and an OpenAI API key. The API requires a small prepaid balance.

Always use a virtual environment, so the packages stay inside this project and do not change your system Python.

```bash
git clone https://github.com/Zeeshan-20/cross-language-rag-assistant.git
cd cross-language-rag-assistant
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

After the activate step, your terminal prompt starts with `(.venv)`. If it does not, do not run `pip install`. Activate first. Every time you open a new terminal, run the `source .venv/bin/activate` line again before running the project.

Create a file named `.env` in the project folder (see `.env.example`):

```
OPENAI_API_KEY=your-key-here
```

Put the four PDFs in `data/`, then run (with `(.venv)` active):

```bash
python3 src/extract.py     # PDFs -> data/pages.json
python3 src/index.py       # chunks -> embeddings -> data/chroma
python3 src/app.py         # start the chat app (open the printed link)
```

Run the first two steps again only when the PDFs change.

## Evaluation

I measure retrieval separately from answer generation. That way I can tell whether a wrong answer came from the search or from the LLM.

- Test set: `eval/questions.json` has 31 questions. 28 have a known correct source page, taken from the documents. 3 have no answer in the documents and must get "not found".
- Metrics: Recall@6 and Recall@3 (is the correct page among the first 6 or 3 results), rank-1 accuracy, and MRR (mean reciprocal rank).
- Run it with `python3 eval/run_eval.py`.

| Retrieval setup | Top 6 | Top 3 | Rank 1 | MRR |
|---|---|---|---|---|
| Plain similarity search | 27/28 | 25/28 | 18/28 | 0.774 |
| + LLM re-ranking (final) | 27/28 | 27/28 | 24/28 | 0.911 |

What changed the numbers:
- Putting the module name at the top of every Modulhandbuch chunk fixed questions where a chunk had lost its module. The Seminar workload question, for example, went from rank 5 to rank 1.
- Transcribing the credit-plan table by hand and storing it as its own chunk made the table questions findable.
- LLM re-ranking raised the correct page at rank 1 from 18 to 24 of 28.
- Query rewriting (English to German) reached MRR 0.923 and fixed the one missed question. I left it out because the gain was small next to the extra cost and waiting time.

## Known limitations

- The evaluation set is small and I used it while developing, so the numbers are probably a little optimistic for new questions.
- The credit-plan table (Studienordnung, Table 1) could not be extracted reliably, so I transcribed it by hand.
- Text is split per PDF page, so a sentence that runs across a page break gets cut.
- One evaluation question is still missed: the one about inspecting exam papers. The English wording differs from the German text.
- Each answer takes several seconds because of the re-ranking step, and costs a small amount of API credit.
- Only the Master Applied Computer Science documents from Hochschule Schmalkalden are included.

  ## Tech stack

Python, OpenAI embeddings and chat model, LangChain (text splitter, OpenAI and Chroma integrations), PyMuPDF,  ChromaDB,  Pydantic, Gradio.

## Project structure

```
src/        extract.py, chunk.py, index.py, retrieve.py, answer.py, app.py
eval/       questions.json, run_eval.py
data/       PDFs and generated files (not committed)
```