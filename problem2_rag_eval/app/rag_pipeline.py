from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTOR_DB_PATH = "../vectordb"


def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )

    return vector_store


def retrieve_documents(query):
    vector_store = load_vector_store()

    results = vector_store.similarity_search(query, k=3)

    return results


if __name__ == "__main__":
    query = input("Enter your question: ")

    docs = retrieve_documents(query)

    print("\nRetrieved Context:\n")

    for idx, doc in enumerate(docs, start=1):
        print(f"\nDocument Chunk {idx}:\n")
        print(doc.page_content)