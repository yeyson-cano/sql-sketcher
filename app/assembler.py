# app/assembler.py

from typing import Dict


def assemble_query(template: str, intent: Dict) -> Dict:
    result = template
    missing = []

    # COLUMN
    if "{{column}}" in result:
        if intent.get("columns"):
            result = result.replace("{{column}}", ", ".join(intent["columns"]))
        else:
            result = result.replace("{{column}}", "UNKNOWN_COLUMN")
            missing.append("column")

    # TABLE
    if "{{table}}" in result:
        if intent.get("tables"):
            result = result.replace("{{table}}", intent["tables"][0])
        else:
            result = result.replace("{{table}}", "UNKNOWN_TABLE")
            missing.append("table")

    # VALUE
    if "{{value}}" in result:
        if intent.get("conditions"):
            val = intent["conditions"][0]["value"]
            if isinstance(val, str):
                val = f"'{val}'"
            result = result.replace("{{value}}", str(val))
        else:
            result = result.replace("{{value}}", "UNKNOWN_VALUE")
            missing.append("value")

    # GROUP_COLUMN
    if "{{group_column}}" in result:
        if intent.get("group_by"):
            result = result.replace("{{group_column}}", intent["group_by"][0])
        else:
            result = result.replace("{{group_column}}", "UNKNOWN_GROUP")
            missing.append("group_column")

    return {
        "query": result,
        "missing_fields": missing
    }
