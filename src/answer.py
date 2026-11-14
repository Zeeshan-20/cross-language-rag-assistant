from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from retrieve import retrieve

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a knowledgeable,expert, friendly assistant representing German university regulations.
You answer questions about German university regulations.
The context below is in German. The question is in English.
Rules:
- Answer in English, using ONLY the context. Do not use outside knowledge.
- Quote the relevant German sentence exactly, in quotation marks.
- After each quote, cite the source as (document title, page).
- If the answer is not in the context, say: "I could not find this in the documents."
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def answer(question):
    docs = retrieve(question)
    context = ""
    for d in docs:
        page = d.metadata["printed_page"] or d.metadata["page"]
        context += f"[{d.metadata['title']}, page {page}]\n{d.page_content}\n\n"
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Context:\n{context}\nQuestion: {question}"),
    ]
    return llm.invoke(messages).content