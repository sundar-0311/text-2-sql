from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from service import ask_database
from database import init_db

from schema_generator import generate_schema_docs
from rag import rebuild_vectorstore

import pandas as pd

from sqlalchemy import create_engine

app = FastAPI(
    title="AI Data Analyst"
)

engine = create_engine(
    "sqlite:///./store.db",
    connect_args={
        "check_same_thread": False
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():

    init_db()


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query(
    req: QueryRequest
):

    if not req.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    return ask_database(
        req.question
    )


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...)
):

    try:

        df = pd.read_csv(
            file.file
        )

        table_name = "uploaded_data"

        df.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False
        )

        schema_docs = generate_schema_docs(
            engine
        )

        rebuild_vectorstore(
            schema_docs
        )

        print("\nGenerated Schema:")
        print(schema_docs)

        return {

            "success": True,

            "message":
                "CSV uploaded successfully",

            "table":
                table_name,

            "rows":
                len(df),

            "columns":
                list(df.columns)

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )