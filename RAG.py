from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def build():

    # 1. Load documents (wiki pages, markdown, PDFs, etc.)
    loader = DirectoryLoader("wiki/",
                            glob="**/*.txt",   # or "*.pdf", etc.
                            loader_cls=TextLoader)  # or PyPDFLoader, etc.
    docs = loader.load()
    # 2. Split into chunks (critical for good retrieval)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # Adjust based on model context
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(docs)
    # 3. Create embeddings + vector store
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./elite_wiki_db"   # For persistence
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",  # or "mmr" for diversity
        search_kwargs={"k": 6}     # Retrieve top 6 chunks
    )

    # 4. LLM
    llm = ChatOllama(
        model="gemma4-pc:latest",
        temperature=0.3,
        # num_ctx=8192 or higher
    )

    # 5. Prompt
    template = """Answer the question based only on the following context.
    If you don't know, say you don't know.
    
    Context: {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 6. RAG Chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Usage
    response = rag_chain.invoke("Give a brief history of FSDs")
    print(response)


def run():
    # Load existing DB
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma(
        persist_directory="./elite_wiki_db",
        embedding_function=embeddings,
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )

    # 4. LLM
    llm = ChatOllama(
        model="gemma4-pc:latest",
        temperature=0.3,
        # num_ctx=8192 or higher
    )

    prompt = ChatPromptTemplate.from_template("""
    Use the provided context to answer the question.

    Context:
    {context}

    Question:
    {question}
    """)

    question = "what is a fuel scoop used for?"
    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    messages = prompt.invoke({
        "context": context,
        "question": question
    })

    response = llm.invoke(messages)

    print(response.content)

run()