from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import pandas as pd
import json


# =========================
# LLM
# =========================

llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0
)


# =========================
# PROMPT
# =========================

chart_prompt = ChatPromptTemplate.from_template("""
You are an expert data visualization assistant.

Question:
{question}

Columns and Data Types:
{columns}

Sample Data:
{sample}

Your task is to determine whether the result should be visualized.

Rules:

1. Use a BAR chart when:
   - One categorical column
   - One numeric column

2. Use a LINE chart when:
   - Time/date column
   - Numeric column

3. Use a PIE chart when:
   - Few categories
   - Represents parts of a whole

4. If the data is not suitable for visualization:
   - Return chartable false

5. Choose the most meaningful columns.

Return ONLY valid JSON.

Chart Example:

{{
  "chartable": true,
  "type": "bar",
  "x": "category_column",
  "y": "numeric_column",
  "title": "Meaningful Chart Title"
}}

Not Chartable Example:

{{
  "chartable": false
}}
""")


# =========================
# CHAIN
# =========================

chart_chain = (
    chart_prompt
    | llm
    | StrOutputParser()
)


# =========================
# MAIN FUNCTION
# =========================

def get_chart_config(
    question: str,
    df: pd.DataFrame
) -> dict:

    try:

        # Column names + dtypes
        column_info = {
            col: str(df[col].dtype)
            for col in df.columns
        }

        # Small sample for the model
        sample_data = df.head(5).to_dict(
            orient="records"
        )

        response = chart_chain.invoke({
            "question": question,
            "columns": json.dumps(
                column_info,
                indent=2
            ),
            "sample": json.dumps(
                sample_data,
                default=str,
                indent=2
            )
        })

        response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        chart_config = json.loads(response)

        required_fields = {
            "chartable"
        }

        if not required_fields.issubset(
            chart_config.keys()
        ):
            return {
                "chartable": False
            }

        return chart_config

    except Exception as e:

        print(
            f"Chart generation failed: {e}"
        )

        return {
            "chartable": False
        }