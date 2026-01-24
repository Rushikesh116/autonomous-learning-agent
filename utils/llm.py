import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env")

    llm = ChatGroq(
        temperature=0.1,
        model="llama-3.3-70b-versatile",
        api_key=api_key  # type: ignore
    )

    return llm