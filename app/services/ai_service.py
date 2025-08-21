from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# just from current directory go two directory up to reach project directory
# this is just know the path of current file then know its directory three times
project_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(project_directory, "data")
book_directory = os.path.join(data_dir, "books")
vector_directory = os.path.join(data_dir, "vectorstores")

# determine model for embedding
embeddings = OllamaEmbeddings(model='nomic-embed-text')

# determine splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

#batch size help not to load all data at once but chunk it then add it
BATCH_SIZE = 100


def answer_about_book(question: str, slug: str):
    return "I am AI assistant"


def search_ai(query: str):
    return "this is list of books match what you need"


def add_book_to_vector_stores(url: str, slug: str):
    if not os.path.exists(url):
        raise FileNotFoundError("The URL you entered doesn't exist")

    persistent_directory = os.path.join(vector_directory, slug)
    if not os.path.exists(persistent_directory):

        loader = PyPDFLoader(url)
        documents = loader.load()

        docs = splitter.split_documents(documents)

        vector_store = Chroma(
            collection_name=slug,
            embedding_function=embeddings,
            persist_directory=persistent_directory,
        )

        for i in range(0, len(docs), BATCH_SIZE):
            batch = docs[i:i + BATCH_SIZE]
            vector_store.add_documents(batch)


def remove_book_from_vector_stores(slug: str):
    pass
