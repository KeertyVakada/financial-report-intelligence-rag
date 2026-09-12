import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


# -------------------------------------------------------------------
# Groq Client
# -------------------------------------------------------------------

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = None

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Add it to your .env file locally or Streamlit Secrets when deployed."
    )

client = Groq(api_key=api_key)


# -------------------------------------------------------------------
# Answer Generation
# -------------------------------------------------------------------

def generate_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate a grounded answer using the retrieved financial evidence.
    """

    if not context.strip():
        return (
            "I don't have enough evidence from the financial report "
            "to answer this question."
        )

    system_prompt = """
You are a financial report question-answering assistant.

Your task is to answer the user's question using ONLY the
financial evidence provided in the context.

Rules:

1. Use only information present in the provided evidence.
2. Do not invent facts, numbers, dates, or explanations.
3. If the evidence does not contain enough information to answer
   the question, clearly say that there is not enough information.
4. When numerical information is available, preserve the exact
   values and units from the evidence.
5. Give a concise and clear answer.
6. Cite the relevant evidence block(s) in your answer using
   references such as [Evidence 1].
"""

    user_prompt = f"""
Financial Evidence:
{context}

Question:
{question}

Answer using only the financial evidence above.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()