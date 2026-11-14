from index import chroma_db

vectorstore = chroma_db()
def retrieve(question, k=6):
    return vectorstore.similarity_search(question, k=k)