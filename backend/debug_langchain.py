import langchain
print(f"LangChain version: {langchain.__version__}")
try:
    from langchain.chains import create_history_aware_retriever
    print("Successfully imported create_history_aware_retriever")
except ImportError as e:
    print(f"Failed to import create_history_aware_retriever: {e}")

try:
    import langchain.chains
    print(f"langchain.chains: {langchain.chains}")
except ImportError as e:
    print(f"Failed to import langchain.chains: {e}")
