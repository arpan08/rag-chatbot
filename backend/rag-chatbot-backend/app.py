import os
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# Load API key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

pdf_folder = "docs"

def load_pdf_documents():
    pdf_docs = []

    pdf_files = [
        os.path.join(pdf_folder, f)
        for f in os.listdir(pdf_folder)
        if f.lower().endswith(".pdf")
    ]

    print("PDF files:", pdf_files)

    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""

            if text.strip():
                pdf_docs.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": pdf_file,
                            "page": i + 1
                        }
                    )
                )

    return pdf_docs


def load_web_docs():
    loader = WebBaseLoader(
        web_paths=["https://en.wikipedia.org/wiki/Current_Procedural_Terminology"]
    )
    return loader.load()


def build_vectorstore():
    pdf_docs = load_pdf_documents()
    web_docs = load_web_docs()

    all_docs = pdf_docs + web_docs

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    splits = splitter.split_documents(all_docs)

    embeddings = OpenAIEmbeddings()

    return Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )


# Build once (important)
vectorstore = build_vectorstore()

rag_prompt = hub.pull("rlm/rag-prompt")

general_prompt = ChatPromptTemplate.from_template("""
Answer normally:

{question}
""")

llm = ChatOpenAI(model="gpt-4o-mini")


def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


def ask_with_fallback(question, threshold=0.6):
    results = vectorstore.similarity_search_with_score(question, k=3)

    if not results:
        return llm.invoke(question).content

    best_score = results[0][1]
    docs = [doc for doc, _ in results]
    context = format_docs(docs)

    if best_score < threshold:
        response = (
            rag_prompt
            | llm
            | StrOutputParser()
        ).invoke({
            "context": context,
            "question": question
        })

        if "NOT_FOUND" not in response:
            return response

    return (
        general_prompt
        | llm
        | StrOutputParser()
    ).invoke({"question": question})