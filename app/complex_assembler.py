# app/complex_assembler.py

from typing import Dict, List
from app.schema_repository import SchemaRepository

def build_join_graph(foreign_keys: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Construye un grafo de relaciones entre tablas a partir de claves foráneas.
    """
    graph = {}
    for fk in foreign_keys:
        from_table = fk["from_table"]
        to_table = fk["to_table"]
        condition = f'{from_table}."{fk["from_column"]}" = {to_table}."{fk["to_column"]}"'
        
        graph.setdefault(from_table, {})[to_table] = condition
        graph.setdefault(to_table, {})[from_table] = condition  # Grafo no dirigido
    return graph

def apply_complex_assembly(
    base_query: str,
    intent: Dict,
    schema_repo: SchemaRepository
) -> Dict:
    """
    Agrega cláusulas JOIN, GROUP BY y HAVING basadas en la intención extraída.
    """
    modified_query = base_query
    notes = []

    tables = intent.get("tables", [])
    joins = []

    # JOINs automáticos si hay múltiples tablas
    if len(tables) > 1:
        graph = build_join_graph(schema_repo.get_foreign_keys())
        base = tables[0]

        for other in tables[1:]:
            if other in graph.get(base, {}):
                join_clause = f' JOIN {other} ON {graph[base][other]}'
                joins.append(join_clause)
                notes.append(f"Join added: {join_clause}")
            else:
                notes.append(f"No join path found from {base} to {other}")

        modified_query += "".join(joins)

    # GROUP BY
    if intent.get("group_by"):
        group_clause = " GROUP BY " + ", ".join(intent["group_by"])
        modified_query += group_clause
        notes.append(f"Group by: {group_clause}")

    # HAVING (simulado si hay agregaciones)
    if intent.get("aggregations"):
        modified_query += " HAVING AVG(score) > 3"
        notes.append("Added HAVING clause: AVG(score) > 3")

    return {
        "query": modified_query,
        "notes": notes
    }
