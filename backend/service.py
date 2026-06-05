from rag import generate_sql
from database import execute_sql
from insights import get_insights
from chart import get_chart_config

import pandas as pd


def ask_database(question: str):

    # Step 1: Generate SQL
    sql = generate_sql(question)

    # Step 2: Execute SQL
    result = execute_sql(sql)

    # Default values
    insights_arr = []
    chart = {
        "chartable": False
    }

    # Step 3: Generate insights and chart
    if result["success"] and result["rows"]:

        df = pd.DataFrame(
            result["rows"]
        )

        insights_arr = get_insights(
            question,
            df
        )

        chart = get_chart_config(
            question,
            df
        )

    # Step 4: Return response
    return {
        "question": question,
        "sql": sql,
        "result": result,
        "insights": insights_arr,
        "chart": chart
    }