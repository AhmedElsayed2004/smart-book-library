from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
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

model = ChatOllama(model='llama3.2', temperature=0)

# determine splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# batch size help not to load all data at once but chunk it then add it
BATCH_SIZE = 100

SYSTEM_MESSAGE = """
You are an expert assistant specialized in answering questions about books using only provided source material.
 Do NOT use external knowledge beyond what is included in the Context. 
 If the answer cannot be determined using the provided excerpts, respond exactly: "I could not find the answer in the provided book excerpts."
"""

HUMAN_MESSAGE = """
CONTEXT (retrieved documents):
{docs}
-- End of Context --

QUESTION:
{question}

INSTRUCTIONS (follow exactly):
1. Base your entire answer only on the passages in "CONTEXT". Do not invent facts or use outside knowledge.
2. If the context contains a clear, direct answer or even partial information, answer concisely (1–4 sentences)
4. If the context is contradictory, explicitly state: "Conflicting information found" and list the differing passages with citations.
5. If no relevant information exists in CONTEXT, reply exactly: "I could not find the answer in the provided book excerpts."
6. Keep the entire response ≤ 400 words unless the user asks for more detail.
"""

messages_template = [
    SystemMessage(content=SYSTEM_MESSAGE),
    ('human', HUMAN_MESSAGE)
]

prompt_template = ChatPromptTemplate.from_messages(messages=messages_template)


async def answer_about_book(question: str, slug: str):
    persistent_directory = os.path.join(vector_directory, slug)

    vector_store = Chroma(
        collection_name=slug,
        embedding_function=embeddings,
        persist_directory=persistent_directory,
    )

    # embede question
    question_embedding = embeddings.embed_query(question)
    import time


    # find most similar parts of the book
    similar_docs = vector_store.similarity_search_by_vector(question_embedding, 20)


    prompt = prompt_template.invoke({'question': question, 'docs': [doc.page_content for doc in similar_docs]})



    async for data in model.astream(prompt):
        yield data.content


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
