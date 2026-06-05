from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from schema_docs import SCHEMA_DOCS
from sqlalchemy import create_engine

import os

# EMBEDDINGS

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# VECTOR STORE

if os.path.exists("./chroma_db") and os.listdir("./chroma_db"):

    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

else:

    vector_store = Chroma.from_texts(
        texts=SCHEMA_DOCS,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )


retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

# LLM

llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0
)

# ENGINE

db_engine = create_engine(
    "sqlite:///./store.db",
    connect_args={"check_same_thread": False}
)

# INTERPRET PROMPT

interpret_prompt = ChatPromptTemplate.from_template("""
You are a database assistant that maps user language to exact database values.

You will be given a user question and the database schema with sample values.
Your job is to rewrite the question replacing any user terms with the EXACT values shown in the Sample Values section of the schema.

Examples:
- User says "kitchen appliance", schema has "Kitchen Appliances" -> use "Kitchen Appliances"
- User says "large", schema has size values "Large, L, XS, S" -> use "Large" or "L" whichever appears
- User says "extra large" -> use "Extra Large" or "XL" whichever appears in schema
- User says "electronic item", schema has "electronics" -> use "electronics"

Rules:
- ONLY replace terms with values that EXACTLY appear in the Sample Values section
- Keep the original intent of the question
- Return ONLY the rewritten question, nothing else
- Do not add explanation

Schema with Sample Values:
{context}

User Question:
{question}

Rewritten Question:
""")

# SQL PROMPT

prompt = ChatPromptTemplate.from_template("""
You are an expert SQL generator for SQLite.

Output ONLY raw SQL.

Do NOT include:
- explanations
- markdown
- backticks

IMPORTANT:
- For ALL string comparisons, always use LOWER() on both sides
  Example: WHERE LOWER(category) = LOWER('Kitchen Appliances')
- ONLY use the exact column names from the schema below
- Do NOT rename, guess, or infer column names
- Always query from the most relevant table based on the question

Relevant Schema:
{context}

Question:
{question}

SQL Query:
""")

# HELPERS

def format_docs(docs):

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )

def get_full_context() -> str:

    from schema_generator import generate_schema_docs

    all_docs = generate_schema_docs(db_engine)

    return "\n\n".join(all_docs)


# INTERPRET USER QUESTION

def interpret_question(
    question: str,
    context: str
) -> str:

    chain = interpret_prompt | llm | StrOutputParser()

    interpreted = chain.invoke({
        "context": context,
        "question": question
    })

    print(f"\n[Interpreted]: {interpreted.strip()}")

    return interpreted.strip()


# BUILD SQL CHAIN (direct, no retriever)

def run_sql_chain(
    question: str,
    context: str
) -> str:

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "context": context,
        "question": question
    })


# BUILD RETRIEVER CHAIN 

def build_sql_chain():

    return (
        {
            "context":
                retriever
                | format_docs,

            "question":
                RunnablePassthrough()
        }

        | prompt
        | llm
        | StrOutputParser()
    )


sql_chain = build_sql_chain()


# GENERATE SQL

def generate_sql(question: str) -> str:

    # Get full context directly from DB
    context = get_full_context()

    print(f"\n[Context sent to interpret]:\n{context}")

    # Interpret user language to DB-friendly terms
    interpreted = interpret_question(
        question.lower(),
        context
    )

    # Generate SQL using full context directly
    sql = run_sql_chain(interpreted, context)

    print(f"\n[Generated SQL]: {sql}")

    return (
        sql
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )


# REBUILD VECTOR STORE

def rebuild_vectorstore(
    schema_docs
):

    global vector_store
    global retriever
    global sql_chain

    # Recreate Chroma DB

    vector_store = Chroma.from_texts(
        texts=schema_docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    # Recreate retriever

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    # Recreate chain

    sql_chain = build_sql_chain()

    print(
        "Vector store rebuilt successfully."
    )

    return True