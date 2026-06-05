from sqlalchemy import inspect, text

def generate_schema_docs(engine):

    inspector = inspect(engine)

    schema_docs = []

    with engine.connect() as conn:

        for table in inspector.get_table_names():

            columns = inspector.get_columns(table)

            column_info = []
            value_info = []

            for col in columns:

                column_info.append(
                    f"{col['name']} ({col['type']})"
                )

                # Get distinct values for each column
                try:
                    result = conn.execute(text(
                        f'SELECT DISTINCT "{col["name"]}" FROM "{table}" LIMIT 10'
                    ))
                    distinct = [
                        str(r[0])
                        for r in result
                        if r[0] is not None
                    ]
                    if distinct:
                        value_info.append(
                            f"  - {col['name']}: {', '.join(distinct)}"
                        )
                except Exception as e:
                    print(f"  [WARN] Could not fetch values for {col['name']}: {e}")

            doc = f"""
Table: {table}

Columns:
{", ".join(column_info)}

Sample Values:
{chr(10).join(value_info) if value_info else "  (no values found)"}
"""

            print(f"\n[Schema Doc Generated]:\n{doc}")  # debug

            schema_docs.append(doc)

    return schema_docs