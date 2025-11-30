import os
from typing import List
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import shutil
import tempfile

# Initialize Embeddings (Local to save cost/complexity)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global variable to store the vector store in memory (for simplicity in this demo)
# In a real app, you might persist this to disk or a DB per session/user.
vector_store = None

async def process_uploaded_files(files: List[UploadFile]):
    global vector_store
    documents = []
    
    # Create a temporary directory to save files for loading
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # Load based on extension
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file.filename.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())
    
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # Create Vector Store
    if splits:
        import asyncio
        from functools import partial
        
        # Run blocking FAISS creation in a separate thread
        loop = asyncio.get_running_loop()
        vector_store = await loop.run_in_executor(
            None, 
            partial(FAISS.from_documents, splits, embeddings)
        )
        return True
    return False

def get_answer(query: str):
    global vector_store
    if not vector_store:
        return "No documents uploaded yet. Please upload files first."
    
    # Setup LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # strict prompt
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If the answer is not in the context, say that you do not know, do NOT try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}
    Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    retriever = vector_store.as_retriever()
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        result = rag_chain.invoke(query)
        return result
    except Exception as e:
        return f"Error generating answer: {str(e)}"
