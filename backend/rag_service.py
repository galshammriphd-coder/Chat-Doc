import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
from functools import partial

class RAGService:
    def __init__(self):
        # Initialize Embeddings (OpenAI for lightweight cloud deployment)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Embeddings will fail.")
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.vector_store = None
        self.vector_store = None
        # self.llm = None # Removed single LLM instance
        # self._initialize_llm() # Removed initialization

    def get_llm(self, model_name: str):
        if model_name.startswith("gpt"):
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API Key is missing.")
            return ChatOpenAI(model_name=model_name, temperature=0, api_key=api_key)
        
        elif model_name.startswith("gemini"):
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Google API Key is missing.")
            return ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key=api_key)
            
        elif model_name.startswith("claude"):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API Key is missing.")
            return ChatAnthropic(model=model_name, temperature=0, api_key=api_key)

        elif model_name.startswith("llama") or model_name.startswith("mixtral"):
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API Key is missing.")
            return ChatGroq(model_name=model_name, temperature=0, api_key=api_key)

        elif model_name == "grok-beta":
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise ValueError("xAI API Key is missing.")
            return ChatOpenAI(model_name=model_name, temperature=0, api_key=api_key, base_url="https://api.x.ai/v1")

        elif model_name == "deepseek-chat":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API Key is missing.")
            return ChatOpenAI(model_name=model_name, temperature=0, api_key=api_key, base_url="https://api.deepseek.com")

        elif model_name.startswith("qwen"):
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DashScope API Key is missing.")
            return ChatOpenAI(model_name=model_name, temperature=0, api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

        elif model_name.startswith("openrouter/"):
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API Key is missing.")
            
            # Strip the prefix to get the actual OpenRouter model ID
            actual_model = model_name.replace("openrouter/", "")
            
            return ChatOpenAI(
                model_name=actual_model, 
                temperature=0, 
                api_key=api_key, 
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:5174",
                    "X-Title": "DocuChat AI",
                }
            )
            
        else:
             raise ValueError(f"Unsupported model: {model_name}")

    async def ingest_files(self, files: List[UploadFile]) -> dict:
        documents = []
        
    async def ingest_files(self, files: List[UploadFile]) -> dict:
        documents = []
        file_details = []
        
        # Ensure uploads directory exists
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            try:
                # Save file persistently
                file_path = os.path.join(upload_dir, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                # Load based on extension
                file_docs = []
                if file.filename.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    file_docs = loader.load()
                elif file.filename.lower().endswith(".txt"):
                    loader = TextLoader(file_path, encoding="utf-8")
                    file_docs = loader.load()
                else:
                    print(f"Skipping unsupported file: {file.filename}")
                    continue

                # Split text for this file to count chunks
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                file_splits = text_splitter.split_documents(file_docs)
                
                documents.extend(file_docs) # Keep original docs for overall processing if needed, or just splits
                
                file_details.append({
                    "name": file.filename,
                    "url": f"http://localhost:8000/uploads/{file.filename}",
                    "chunks": len(file_splits)
                })

            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                return {"success": False, "error": f"Error processing {file.filename}: {str(e)}"}
        
        if not documents:
            return {"success": False, "error": "No valid documents found to process."}

        # Split all text for vector store
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        if not splits:
             return {"success": False, "error": "Documents were empty after processing."}

        # Create Vector Store (Blocking operation run in thread)
        try:
            loop = asyncio.get_running_loop()
            self.vector_store = await loop.run_in_executor(
                None, 
                partial(FAISS.from_documents, splits, self.embeddings)
            )
            return {
                "success": True, 
                "count": len(documents),
                "files": file_details
            }
        except Exception as e:
             return {"success": False, "error": f"Failed to create vector store: {str(e)}"}

    def query(self, question: str, model_name: str = "gpt-3.5-turbo", chat_history: List[dict] = []) -> str:
        if not self.vector_store:
            return "Please upload documents first to start chatting."
        
        try:
            llm = self.get_llm(model_name)
        except ValueError as e:
            return str(e)

        # Convert simple dict history to LangChain messages
        history_messages = []
        for msg in chat_history:
            if msg.get("role") == "user":
                history_messages.append(HumanMessage(content=msg.get("content")))
            elif msg.get("role") == "assistant":
                history_messages.append(AIMessage(content=msg.get("content")))

        retriever = self.vector_store.as_retriever()

        # 1. Contextualize question prompt (if history exists)
        contextualize_q_system_prompt = """Given a chat history and the latest user question 
        which might reference context in the chat history, formulate a standalone question 
        which can be understood without the chat history. Do NOT answer the question, 
        just reformulate it if needed and otherwise return it as is."""
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # 2. Answer question prompt
        system_prompt = """You are a smart assistant designed and trained by Dr. Ghaleb Al-Shammari.
        If the user asks about your identity or who you are, respond exactly with: "انا مساعدك الذكي تم تصميمي وتدريبي بواسطة د. غالب الشمري".

        For all other questions, use the following pieces of context to answer the question at the end. 
        If the answer is not in the context, say that you do not know, do NOT try to make up an answer.
        
        Context:
        {context}"""
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        try:
            # Invoke the chain
            result = rag_chain.invoke({
                "input": question,
                "chat_history": history_messages
            })
            return result["answer"]
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg and "data policy" in error_msg:
                return (
                    "**OpenRouter Error**: Your account data policy does not match the model's requirements.\n\n"
                    "Please visit [OpenRouter Settings](https://openrouter.ai/settings/privacy) and enable "
                    "**'Allow model training'** for free models, or choose a paid model."
                )
            return f"Error generating answer: {error_msg}"

    def clear(self):
        self.vector_store = None
