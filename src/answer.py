from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from retrieve import retrieve

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a friendly, expert assistant for German university regulations.
You answer questions about German university regulations.
The context below is in German. The question is in English.
Rules:
- If the user greets you, introduces themselves, thanks you, or makes small talk, reply in one short sentence. Mention what you can do only in your first reply of the chat.
- If the user asks who you are, which university you work for, what you can do, or how you can help, answer in two sentences: you are an assistant for the study, module and exam regulations of the Master Applied Computer Science at Hochschule Schmalkalden, and you answer English questions about these German documents with quotes and page numbers. You are an unofficial student project and not legal advice.
- Only if the user explicitly asks about the chat itself (for example "what is my name?" or "what did I ask before?"), answer from the section "Earlier conversation" in one short sentence. Do not use the documents for this.
- For questions about the regulations: answer in English, using ONLY the context. Do not use outside knowledge.
- Quote the relevant German sentence exactly, in quotation marks.
- After each quote, cite the source as (document title, page).
- If a question about the regulations is not answered in the context, say: "I could not find this in the documents."
- Never end an answer with a question or an offer such as "How can I assist you?".
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# MODEL = "gpt-6-luna"   # comment out  this  line when OpenAI retires a model
# llm = ChatOpenAI(model=MODEL)

def make_standalone(question, history):
    """Turn a follow-up question into a full question that can be searched."""
    if not history:
        return question
    past = ""
    for q, a in history[-3:]:
        past += f"User: {q}\nAssistant: {a}\n"
    prompt = (
        "Rewrite the last question so it can be understood without the conversation. "
        "Keep it in English. Return only the question.\n\n"
        f"Conversation:\n{past}\nLast question: {question}"
    )
    return llm.invoke(prompt).content.strip()


def answer(question, history=None):
    history = history or []
    search_question = make_standalone(question, history)
    docs = retrieve(search_question)

    context = ""
    for d in docs:
        page = d.metadata["printed_page"] or d.metadata["page"]
        context += f"[{d.metadata['title']}, page {page}]\n{d.page_content}\n\n"

    past = ""
    for q, a in history[-4:]:
        past += f"User: {q}\nAssistant: {a}\n"
    if not past:
        past = "(none)"

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Earlier conversation:\n{past}\n"
                  f"Context from the documents:\n{context}\n"
                  f"Question: {question}"),
    ]
    return llm.invoke(messages).content