from typing import Dict
from app.schema_repository import SchemaRepository
from app.llm_helper import complete_placeholders_with_llm
from app.assembler import assemble_query
from app.join_resolver import suggest_join_info

PLACEHOLDER_KEYS = ["UNKNOWN_TABLE", "UNKNOWN_COLUMN", "UNKNOWN_GROUP", "UNKNOWN_VALUE"]

def has_placeholders(sql: str) -> bool:
    return any(ph in sql for ph in PLACEHOLDER_KEYS)

def ensure_quoted_ident(val: str) -> str:
    """
    Asegura que un identificador esté entre comillas dobles.
    """
    if val.startswith('"') and val.endswith('"'):
        return val
    return f'"{val}"'

async def apply_complex_assembly(
    partial_query: str,
    intent: Dict,
    nl_input: str,
    schema_repo: SchemaRepository
) -> Dict:
    """
    Completa placeholders faltantes y resuelve JOINs con ayuda del LLM.
    """
    notes = []
    schema_dict = schema_repo.get_schema_dict()

    # Paso 1: Si no hay placeholders, devolver tal cual
    if not has_placeholders(partial_query):
        notes.append("✅ No enrichment needed.")
        return {
            "query": partial_query,
            "notes": notes
        }

    # Paso 2: Completar placeholders
    llm_result = await complete_placeholders_with_llm(
        user_query=nl_input,
        partial_sql=partial_query,
        schema=schema_dict["columns"]
    )

    if "error" in llm_result:
        notes.append(f"⚠️ Enrichment failed: {llm_result['error']}")
        return {
            "query": partial_query,
            "notes": notes
        }

    overrides = {
        key: ensure_quoted_ident(value) if key in {"table", "column", "group_column", "agg_column"} else value
        for key, value in llm_result.items()
    }

    enriched = assemble_query(partial_query, intent, overrides)

    if enriched["missing_fields"]:
        notes.append("⚠️ Some fields are still missing after enrichment.")

    # Paso 3: Verificar si hay columnas externas (JOIN implícito)
    main_table = overrides.get("table", None)
    all_columns = schema_dict

    used_columns = []
    if "column" in overrides:
        used_columns += [overrides["column"]]
    if "agg_column" in overrides:
        used_columns += [overrides["agg_column"]]
    if "group_column" in overrides:
        used_columns += [overrides["group_column"]]

    # Revisar si alguna columna pertenece a otra tabla
    for col in used_columns:
        col_clean = col.strip('"')
        if main_table:
            main_table_clean = main_table.strip('"')
            if col_clean not in all_columns.get(main_table_clean, []):
                # Buscar sugerencia de JOIN
                join_suggestion = await suggest_join_info(nl_input, col_clean, main_table_clean, all_columns)

                if "join_table" in join_suggestion and "join_condition" in join_suggestion:
                    join_clause = f' JOIN "{join_suggestion["join_table"]}" ON {join_suggestion["join_condition"]}'
                    enriched["query"] = enriched["query"].replace("FROM " + main_table, f'FROM {main_table}{join_clause}')
                    notes.append(f"🔗 Auto JOIN added with {join_suggestion['join_table']}")
                else:
                    notes.append(f"⚠️ No JOIN could be resolved for column: {col_clean}")

    return {
        "query": enriched["query"],
        "notes": notes
    }
