# app/assembler.py

from typing import Dict

def quote_ident(name: str) -> str:
    """
    Añade comillas dobles a identificadores SQL, escapando comillas internas si fuera necesario.
    """
    return f'"{name.replace("\"", "\"\"")}"'

def assemble_query(template: str, intent: Dict) -> Dict:
    result = template
    missing = []

    # COLUMN
    if "{{column}}" in result:
        if intent.get("columns"):
            columns = ", ".join([quote_ident(c) for c in intent["columns"]])
            result = result.replace("{{column}}", columns)
        else:
            result = result.replace("{{column}}", "UNKNOWN_COLUMN")
            missing.append("column")

    # TABLE
    if "{{table}}" in result:
        if intent.get("tables"):
            result = result.replace("{{table}}", quote_ident(intent["tables"][0]))
        else:
            result = result.replace("{{table}}", "UNKNOWN_TABLE")
            missing.append("table")

    # VALUE
    if "{{value}}" in result:
        if intent.get("conditions"):
            val = intent["conditions"][0]["value"]
            if isinstance(val, str):
                val = f"'{val.replace('\'', '\'\'')}'"  # escapa comillas simples
            result = result.replace("{{value}}", str(val))
        else:
            result = result.replace("{{value}}", "UNKNOWN_VALUE")
            missing.append("value")

    # GROUP_COLUMN
    if "{{group_column}}" in result:
        if intent.get("group_by"):
            group = quote_ident(intent["group_by"][0])
            result = result.replace("{{group_column}}", group)
        else:
            result = result.replace("{{group_column}}", "UNKNOWN_GROUP")
            missing.append("group_column")

    return {
        "query": result,
        "missing_fields": missing
    }
