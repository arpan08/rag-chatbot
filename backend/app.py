import os
import requests
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


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Please add it in your .env file.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
pdf_folder = "docs"

JAVA_TOOL_BASE_URL = "http://localhost:8081"

llm = ChatOpenAI(model="gpt-4o-mini")


# ---------------------------------------------------------
# Load PDF documents
# ---------------------------------------------------------
def load_pdf_documents():
    pdf_docs = []

    if not os.path.exists(pdf_folder):
        print(f"PDF folder '{pdf_folder}' does not exist.")
        return pdf_docs

    pdf_files = [
        os.path.join(pdf_folder, f)
        for f in os.listdir(pdf_folder)
        if f.lower().endswith(".pdf")
    ]

    print("PDF files:", pdf_files)

    for pdf_file in pdf_files:
        try:
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

        except Exception as e:
            print(f"Error reading PDF file {pdf_file}: {e}")

    return pdf_docs


# ---------------------------------------------------------
# Load web documents
# ---------------------------------------------------------
def load_web_docs():
    try:
        loader = WebBaseLoader(
            web_paths=[
                "https://en.wikipedia.org/wiki/Current_Procedural_Terminology"
            ]
        )
        return loader.load()

    except Exception as e:
        print(f"Error loading web docs: {e}")
        return []


# ---------------------------------------------------------
# Build vector store
# ---------------------------------------------------------
def build_vectorstore():
    pdf_docs = load_pdf_documents()
    web_docs = load_web_docs()

    all_docs = pdf_docs + web_docs

    if not all_docs:
        raise ValueError("No documents found. Please add PDFs inside docs folder or check web loader.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    splits = splitter.split_documents(all_docs)

    embeddings = OpenAIEmbeddings()

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )

    print(f"Vectorstore created with {len(splits)} chunks.")

    return vectorstore


# ---------------------------------------------------------
# Build vectorstore once during app startup
# ---------------------------------------------------------
vectorstore = build_vectorstore()


# ---------------------------------------------------------
# Prompts
# ---------------------------------------------------------
rag_prompt = hub.pull("rlm/rag-prompt")

general_prompt = ChatPromptTemplate.from_template("""
Answer the question normally and clearly.

Question:
{question}
""")


# ---------------------------------------------------------
# Helper: format retrieved docs
# ---------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


# ---------------------------------------------------------
# RAG with fallback
# Important:
# Chroma returns distance score.
# Lower score usually means more similar.
# So threshold logic here means:
# score <= threshold => relevant enough for RAG
# score > threshold => not relevant, use general LLM
# ---------------------------------------------------------
def ask_with_fallback(question, threshold=0.6):
    results = vectorstore.similarity_search_with_score(question, k=3)

    if not results:
        return (
            general_prompt
            | llm
            | StrOutputParser()
        ).invoke({"question": question})

    best_score = results[0][1]

    print("Best similarity score:", best_score)

    docs = [doc for doc, score in results]

    # If score is low enough, use RAG context
    if best_score <= threshold:
        context = format_docs(docs)

        return (
            rag_prompt
            | llm
            | StrOutputParser()
        ).invoke({
            "context": context,
            "question": question
        })

    # If no good document match, answer normally
    return (
        general_prompt
        | llm
        | StrOutputParser()
    ).invoke({"question": question})


# ---------------------------------------------------------
# Java Tool Calls
# ---------------------------------------------------------
def call_time_tool(zone="Asia/Kolkata"):
    try:
        response = requests.get(
            f"{JAVA_TOOL_BASE_URL}/tools/time",
            params={"zone": zone},
            timeout=5
        )

        response.raise_for_status()
        return response.text

    except Exception as e:
        print("Time tool error:", e)
        return "Unable to fetch current time right now."


def call_date_tool():
    try:
        response = requests.get(
            f"{JAVA_TOOL_BASE_URL}/tools/date",
            timeout=5
        )

        response.raise_for_status()
        return response.text

    except Exception as e:
        print("Date tool error:", e)
        return "Unable to fetch today's date right now."


def call_weather_tool(city="Bangalore"):
    try:
        response = requests.get(
            f"{JAVA_TOOL_BASE_URL}/tools/weather",
            params={"city": city},
            timeout=5
        )

        response.raise_for_status()
        return response.text

    except Exception as e:
        print("Weather tool error:", e)
        return f"Unable to fetch weather for {city} right now."


def call_calculator_tool(a, b, operation):
    try:
        response = requests.get(
            f"{JAVA_TOOL_BASE_URL}/tools/calculate",
            params={
                "a": a,
                "b": b,
                "operation": operation
            },
            timeout=5
        )

        response.raise_for_status()
        return response.text

    except Exception as e:
        print("Calculator tool error:", e)
        return "Unable to calculate right now."


# ---------------------------------------------------------
# Simple city extraction for weather
# Example:
# "weather in Kolkata" -> Kolkata
# "what is the weather in Bangalore" -> Bangalore
# ---------------------------------------------------------
def extract_city(question):
    q = question.lower()

    if "weather in" in q:
        city = question.lower().split("weather in", 1)[1].strip()
        return city.title()

    if "temperature in" in q:
        city = question.lower().split("temperature in", 1)[1].strip()
        return city.title()

    return "Bangalore"


# ---------------------------------------------------------
# Simple calculator routing
# Example:
# "add 10 and 5"
# "multiply 10 and 5"
# ---------------------------------------------------------
def try_calculator(question):
    q = question.lower()

    operation = None

    if "add" in q or "sum" in q or "plus" in q:
        operation = "add"
    elif "subtract" in q or "minus" in q:
        operation = "subtract"
    elif "multiply" in q or "into" in q:
        operation = "multiply"
    elif "divide" in q:
        operation = "divide"

    if not operation:
        return None

    numbers = []

    for word in q.replace(",", " ").split():
        try:
            numbers.append(float(word))
        except ValueError:
            pass

    if len(numbers) >= 2:
        return call_calculator_tool(numbers[0], numbers[1], operation)

    return None


# ---------------------------------------------------------
# Main Router
# This decides whether to call:
# 1. Java tool service
# 2. RAG
# 3. General LLM fallback
# ---------------------------------------------------------
def route_question(question):
    q = question.lower()

    # Time tool
    if "time" in q or "what time" in q:
        return call_time_tool("Asia/Kolkata")

    # Date tool
    if "date" in q or "today" in q:
        return call_date_tool()

    # Weather toolj
    if "weather" in q or "temperature" in q:
        city = extract_city(question)
        return call_weather_tool(city)

    # Calculator tool
    calculator_response = try_calculator(question)
    if calculator_response:
        return calculator_response

    # Default RAG
    return ask_with_fallback(question)