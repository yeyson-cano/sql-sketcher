from typing import Dict, Optional

def quote_ident(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'

def format_value(val):
    if isinstance(val, str):
        escaped = val.replace("'", "''")
        return f"'{escaped}'"
    return str(val)

def assemble_query(
    template: str,
    intent: Dict,
    overrides: Optional[Dict[str, str]] = None
) -> Dict:
    result = template
    missing = []

    overrides = overrides or {}

    # COLUMN
    if "{{column}}" in result:
        if "column" in overrides:
            result = result.replace("{{column}}", overrides["column"])
        elif any(func in template for func in ["AVG({{column}})", "SUM({{column}})", "COUNT({{column}})"]):
            aggs = intent.get("aggregations", [])
            if aggs and isinstance(aggs[0], dict) and "column" in aggs[0]:
                result = result.replace("{{column}}", quote_ident(aggs[0]["column"]))
            else:
                result = result.replace("{{column}}", "UNKNOWN_AGG_COLUMN")
                missing.append("column")
        elif intent.get("columns"):
            result = result.replace("{{column}}", ", ".join([quote_ident(c) for c in intent["columns"]]))
        else:
            result = result.replace("{{column}}", "UNKNOWN_COLUMN")
            missing.append("column")

    # TABLE
    if "{{table}}" in result:
        if "table" in overrides:
            result = result.replace("{{table}}", overrides["table"])
        elif intent.get("tables"):
            result = result.replace("{{table}}", quote_ident(intent["tables"][0]))
        else:
            result = result.replace("{{table}}", "UNKNOWN_TABLE")
            missing.append("table")

    # VALUE
    if "{{value}}" in result:
        if "value" in overrides:
            result = result.replace("{{value}}", overrides["value"])
        elif intent.get("conditions"):
            val = intent["conditions"][0].get("value")
            if val is not None:
                result = result.replace("{{value}}", format_value(val))
            else:
                result = result.replace("{{value}}", "UNKNOWN_VALUE")
                missing.append("value")
        else:
            result = result.replace("{{value}}", "UNKNOWN_VALUE")
            missing.append("value")

    # GROUP_COLUMN
    if "{{group_column}}" in result:
        if "group_column" in overrides:
            result = result.replace("{{group_column}}", overrides["group_column"])
        elif intent.get("group_by"):
            result = result.replace("{{group_column}}", quote_ident(intent["group_by"][0]))
        else:
            result = result.replace("{{group_column}}", "UNKNOWN_GROUP")
            missing.append("group_column")

    # AGG_FUNC
    if "{{agg_func}}" in result:
        if "agg_func" in overrides:
            result = result.replace("{{agg_func}}", overrides["agg_func"])
        elif intent.get("aggregations"):
            func = intent["aggregations"][0].get("function")
            if func:
                result = result.replace("{{agg_func}}", func.upper())
            else:
                result = result.replace("{{agg_func}}", "UNKNOWN_AGG")
                missing.append("agg_func")
        else:
            result = result.replace("{{agg_func}}", "UNKNOWN_AGG")
            missing.append("agg_func")

    # AGG_COLUMN
    if "{{agg_column}}" in result:
        if "agg_column" in overrides:
            result = result.replace("{{agg_column}}", overrides["agg_column"])
        elif intent.get("aggregations"):
            col = intent["aggregations"][0].get("column")
            if col:
                result = result.replace("{{agg_column}}", quote_ident(col))
            else:
                result = result.replace("{{agg_column}}", "UNKNOWN_AGG_COLUMN")
                missing.append("agg_column")
        else:
            result = result.replace("{{agg_column}}", "UNKNOWN_AGG_COLUMN")
            missing.append("agg_column")

    return {
        "query": result,
        "missing_fields": missing
    }
