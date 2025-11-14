from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os


load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

pdf_path=Path(__file__).parent/"DSA.pdf"

#Load this file in the current program
loader=PyPDFLoader(file_path=pdf_path)
docs=loader.load()
#print(docs[5])

#Split the Docs into smaller chunks
text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400 #It will help us to get some information about previous chunk and current chunk also
)

chunks=text_splitter.split_documents(documents=docs)

#Vector Embeddings for this chunks
embedding_model=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

vector_store=QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="Learning_Rag"
)

print("Indexing of Document Done......")
