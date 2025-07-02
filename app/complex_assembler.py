# app/complex_assembler.py

from typing import Dict, List

# Simulación de relaciones para JOIN
schema_graph = {
    "students": {"grades": "students.id = grades.student_id"},
    "grades": {"students": "grades.student_id = students.id"},
    "courses": {"grades": "courses.id = grades.course_id"},
}

def apply_complex_assembly(base_query: str, intent: Dict) -> Dict:
    modified_query = base_query
    notes = []

    tables = intent.get("tables", [])
    joins = []

    # Construir JOINs si hay más de una tabla
    if len(tables) > 1:
        base = tables[0]
        modified_query = modified_query.replace("FROM " + base, f"FROM {base}")
        for other in tables[1:]:
            if other in schema_graph.get(base, {}):
                condition = schema_graph[base][other]
                join_clause = f" JOIN {other} ON {condition}"
                joins.append(join_clause)
                notes.append(f"Join added: {join_clause}")
            else:
                notes.append(f"No join path from {base} to {other}")
        modified_query += "".join(joins)

    # Agregar GROUP BY si aplica
    if intent.get("group_by"):
        group_clause = " GROUP BY " + ", ".join(intent["group_by"])
        modified_query += group_clause
        notes.append(f"Group by: {group_clause}")

    # Agregar HAVING si hay condiciones sobre agregados (simulado)
    if intent.get("aggregations"):
        modified_query += " HAVING AVG(score) > 3"  # Simulación
        notes.append("Added HAVING clause: AVG(score) > 3")

    return {
        "query": modified_query,
        "notes": notes
    }
