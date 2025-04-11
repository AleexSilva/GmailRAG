# imports
from decouple import config
import os
import gradio as gr
from openai import OpenAI
import pandas as pd

# imports for langchain

from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


MODEL = "gpt-4o-mini"
openai_api_key = config('OPENAI_API_KEY')


if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")


# Path to emails.csv
CSV_PATH = os.path.join("..", "input", "emails.csv")

# Load emails from CSV
df = pd.read_csv(CSV_PATH)

# Check structure
print(f"📄 Loaded {len(df)} emails from {CSV_PATH}")
print("Columns:", df.columns.tolist())

# Convert each email into a LangChain Document
documents = []
for _, row in df.iterrows():
    content = f"""
    Email Type: {row['type']}
    Subject: {row['subject']}
    From/To: {row['sender']}
    Date: {row['date']}
    
    Content:
    {row['snippet']}
    """
    metadata = {"id": row["id"], "type": row["type"], "date": row["date"]}
    documents.append(Document(page_content=content.strip(), metadata=metadata))

print(f"📚 Created {len(documents)} documents from emails.")

# Split into chunks
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(documents)

print(f"🔍 Total chunks created: {len(chunks)}")


embeddings = OpenAIEmbeddings(api_key = openai_api_key)

# Create FAISS vector store
vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

# Optionally, save the FAISS index
faiss_path = os.path.join("..", "input", "emails_faiss_index")
vectorstore.save_local(faiss_path)

print(f"✅ FAISS index saved to: {faiss_path}")

# Let's investigate the vectors
total_vectors = vectorstore.index.ntotal
dimensions = vectorstore.index.d

print(f"There are {total_vectors} vectors with {dimensions:,} dimensions in the vector store")


# create a new Chat with OpenAI
llm = ChatOpenAI(temperature=0.7, model_name=MODEL, api_key = openai_api_key)

# set up the conversation memory for the chat
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

# the retriever is an abstraction over the VectorStore that will be used during RAG
retriever = vectorstore.as_retriever(search_kwargs={"k": 25})

# putting it together: set up the conversation chain with the GPT 3.5 LLM, the vector store and memory
conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)

# Let's try a simple question

def chat(question, history):
    result = conversation_chain.invoke({"question": question})
    return result["answer"]

view = gr.ChatInterface(chat, type="messages").launch()
