from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from index import chroma_db

vectorstore = chroma_db()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class RankOrder(BaseModel):
    order: list[int]                          # chunk ids, most relevant first


def rerank(question, chunks):
    prompt = (
        "The question is in English. The chunks are German excerpts from university regulations. "
        "Order ALL chunks by how well they answer the question, most relevant first. "
        f"Question: {question}\n\n"
    )
    for i, c in enumerate(chunks, start=1):
        prompt += f"# CHUNK ID {i}\n{c.page_content}\n\n"

    order = llm.with_structured_output(RankOrder).invoke(prompt).order
    order = [i for i in order if 1 <= i <= len(chunks)]
    return [chunks[i - 1] for i in order]


def retrieve(question, k=6):
    chunks = vectorstore.similarity_search(question, k=15)
    return rerank(question, chunks)[:k]