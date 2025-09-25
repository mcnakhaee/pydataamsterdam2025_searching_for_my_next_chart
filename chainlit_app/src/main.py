from chainlit import Chainlit

def main():
    app = Chainlit()
    
    # Initialize Weaviate client and other configurations
    from rag.weaviate_client import WeaviateClient
    from rag.document_loader import DocumentLoader
    from rag.retriever import Retriever

    weaviate_client = WeaviateClient()
    document_loader = DocumentLoader()
    retriever = Retriever(weaviate_client)

    # Load documents into the application
    documents = document_loader.load_documents()
    retriever.index_documents(documents)

    # Start the Chainlit application
    app.run()

if __name__ == "__main__":
    main()