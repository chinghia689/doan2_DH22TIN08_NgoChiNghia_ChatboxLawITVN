import os
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.runnables import RunnableLambda, RunnableParallel

def deduplicate_docs(data):
    bm25_docs=data.get('bm25',[])
    chroma_docs=data.get('chroma',[])

    unique_docs=[]
    seen_content=set()

    for doc in bm25_docs:
        if doc.page_content not in seen_content:
            unique_docs.append(doc)
            seen_content.add(doc.page_content)

    for doc in chroma_docs:
        if doc.page_content not in seen_content:
            unique_docs.append(doc)
            seen_content.add(doc.page_content)
    return unique_docs

def retriever(docs,embeddings,persist_dir="./chroma_db"):
    if os.path.exists(persist_dir):
        chroma=Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
    else:
        chroma=Chroma.from_documents(
            docs,
            embedding=embeddings,
            persist_directory=persist_dir
        )
    chroma_retriever=chroma.as_retriever(search_kwargs={'k':10})

    bm25_retriever=BM25Retriever.from_documents(docs)
    bm25_retriever.k=10

    retriever=RunnableParallel(
        vector=chroma_retriever,
        bm25=bm25_retriever
    )|RunnableLambda(deduplicate_docs)

    return retriever


