from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_MODEL, VECTOR_DB_PATH, VECTOR_COLLECTION_NAME
from logger import log


def retrieve(indexed_records, retrieval_query, top_k):
    log("retrieve")
    retriever = indexed_records.as_retriever(
        search_kwargs={"k": top_k},
    )
    retrieved_chunks = retriever.invoke(retrieval_query)
    return retrieved_chunks


def get_vector_store():
    log("get_vector_store")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vector_store = Chroma(
        collection_name=VECTOR_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PATH,
        collection_metadata={"hnsw:space": "cosine"}
    )

    return vector_store


def get_vector_counts():
    log("get_vector_counts")
    vector_store = get_vector_store()
    return vector_store._collection.count()
