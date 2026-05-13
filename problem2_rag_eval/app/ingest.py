from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "../data"
VECTOR_DB_PATH = "../vectordb"


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)
    return chunks


def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    vector_store.persist()

    print("Vector database created successfully!")


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)

    print(f"Loaded {len(docs)} documents")
    print(f"Created {len(chunks)} chunks")

    create_vector_store(chunks)