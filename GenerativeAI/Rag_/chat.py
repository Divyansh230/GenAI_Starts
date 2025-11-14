import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load ENV
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Embeddings (Gemini)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# Connect to Qdrant
vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="Learning_Rag"
)

# Take user query
user_query = input("Ask Something... ")

# Retrieve relevant chunks
search_results = vector_db.similarity_search(query=user_query, k=4)

# Prepare context
context = "\n\n".join([
    f"Page Content: {result.page_content}\n"
    f"Page Number: {result.metadata.get('page_label')}\n"
    f"File Location: {result.metadata.get('source')}"
    for result in search_results
])

# System prompt
SYSTEM_PROMPT = """
You are a helpful assistant who answers the user query ONLY using the given context.
Do NOT hallucinate.  
If the answer is not in the context, say:
"I couldn't find the answer in the provided document."

Also guide the user to the correct page number.

Context:
{context}
"""

# Build prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{query}")
])

# Gemini 2.5 Flash model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Build chain
chain = prompt | model

# Get final output
response = chain.invoke({
    "context": context,
    "query": user_query
})

print("\n\n===== Answer =====\n")
print(response.content)
