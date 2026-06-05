from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
import json

llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0
)

insight_prompt = ChatPromptTemplate.from_template("""
You are an expert data analyst.

Question:
{question}

Columns:
{columns}

Summary:
{summary}

Sample Data:
{sample}

Rules:
1. Generate 3 concise insights.
2. Use actual values from the data.
3. Do not invent facts.
4. Output ONLY a JSON array.
5. No markdown.

Example:
["Average age is 35.", "Bob Smith is the oldest user at 45 years."]
""")

insight_chain= (
  insight_prompt
  | llm
  | StrOutputParser()
)

def get_insights(question: str, df: pd.DataFrame):
    try:
        response = insight_chain.invoke({
            "question": question,
            "columns": list(df.columns),
            "summary": df.describe(include="all").to_string(),
            "sample": json.dumps(
                df.head(5).to_dict(orient="records"),
                default=str
            )
        })

        response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(response)

    except Exception as e:
        return [f"Insight generation failed: {e}"]