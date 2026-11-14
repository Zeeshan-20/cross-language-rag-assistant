import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chunk import make_chunks

load_dotenv(override=True)

db_name = "data/chroma"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def build_index():
    chunks = make_chunks()
    print(len(chunks), "chunks")

    if os.path.exists(db_name):
        Chroma(persist_directory=db_name, embedding_function=embeddings).delete_collection()

    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=db_name
    )
    print(vectorstore._collection.count(), "chunks in Chroma")
    return vectorstore


def chroma_db():
    return Chroma(persist_directory=db_name, embedding_function=embeddings)


if __name__ == "__main__":
    build_index()