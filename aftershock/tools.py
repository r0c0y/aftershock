"""The agent's graph tools. Every one is a real Cypher query against FalkorDB.

Edge directions (child points at what it depends on):
  (Decision)-[:BASED_ON]->(Fact)      (Answer)-[:DERIVED_FROM]->(Decision|Fact)
  (Fact)-[:DERIVED_FROM]->(Fact)      (Task)-[:IMPLEMENTS]->(Decision)
  (Fact)-[:STATED_IN]->(Document)     (Fact)-[:CORRECTED_BY]->(Fact)
"""
import datetime as dt
from .db import graph, rows
from . import seed_data as S

DEP = "BASED_ON|DERIVED_FROM|IMPLEMENTS"
KIND_ORDER = {"Fact": 0, "Decision": 1, "Answer": 2, "Task": 3}

Q_CORRECT_NEW = """
MATCH (old:Fact {id:$old}), (doc:Document {id:$doc})
CREATE (new:Fact {id:$new, text:$text, status:'current', valid_from:$now, valid_to:''})
CREATE (new)-[:STATED_IN]->(doc)
CREATE (old)-[:CORRECTED_BY {at:$now, note:$note}]->(new)
SET old.status = 'superseded', old.valid_to = $now
RETURN new.id AS id"""

# Everything downstream of the stale fact, with every dependency path (variable length, 1..5 hops).
Q_BLAST = """
MATCH p=(f:Fact {id:$id})<-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*1..5]-(x)
RETURN x.id AS id, labels(x)[0] AS kind, min(length(p)) AS hops"""

# Evidence chain: shortest dependency path from the affected node back to the stale fact,
# then the source document where the stale fact was stated.
Q_PATH = """
MATCH (x {id:$x}), (f:Fact {id:$f})
RETURN [n IN nodes(shortestPath((x)-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*..6]->(f))) | n.id] AS ids,
       [n IN nodes(shortestPath((x)-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*..6]->(f))) | coalesce(n.title, n.text)] AS labels,
       [r IN relationships(shortestPath((x)-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*..6]->(f))) | type(r)] AS rels"""

Q_DETAIL = """
MATCH (x {id:$id})
OPTIONAL MATCH (p:Person)-[:OWNS]->(x)
OPTIONAL MATCH (x)-[:RECORDED_IN]->(d:Document)
RETURN labels(x)[0] AS kind, coalesce(x.title, x.text) AS label, x.status AS status, x.rationale AS rationale,
       coalesce(p.name, d.author) AS owner, d.id AS doc_id, d.title AS doc_title"""

Q_SOURCES = """
MATCH (f:Fact {id:$id})-[:STATED_IN]->(d:Document)
RETURN d.id AS id, d.title AS title, d.state AS state ORDER BY d.date"""

def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_fact(fid):
    r = rows(graph().query("MATCH (f:Fact {id:$id}) RETURN f.id AS id, f.text AS text, f.status AS status", {"id": fid}))
    return r[0] if r else None

def current_facts():
    return rows(graph().query("MATCH (f:Fact) RETURN f.id AS id, f.text AS text, f.status AS status ORDER BY f.id"))

def blast_radius(fact_id):
    """Tool 2. All Facts/Decisions/Answers/Tasks that depend on fact_id, with hop count."""
    return sorted(rows(graph().query(Q_BLAST, {"id": fact_id})), key=lambda r: (r["hops"], KIND_ORDER[r["kind"]], r["id"]))

def path_proof(fact_id, node_id):
    """Tool 3. The literal dependency path (and source documents) from a node back to the stale fact."""
    g = graph()
    r = rows(g.query(Q_PATH, {"x": node_id, "f": fact_id}))
    path = r[0] if r else {"ids": [], "labels": [], "rels": []}
    path["sources"] = rows(g.query(Q_SOURCES, {"id": fact_id}))
    return path

def correct_fact(fact_id, new_fact_id, new_text, source_doc, note=""):
    """Tool 1. Supersede, never delete: new Fact + CORRECTED_BY edge; old Fact gets valid_to."""
    g = graph()
    t = now()
    g.query(Q_CORRECT_NEW, {"old": fact_id, "new": new_fact_id, "text": new_text, "doc": source_doc, "now": t, "note": note})
    g.query("MATCH (d:Document {id:$d}) SET d.state = 'executed'", {"d": source_doc})
    return {"old": fact_id, "new": new_fact_id, "at": t}

def flag_stale(fact_id):
    """Mark everything downstream as stale (kept in the graph, nothing deleted). Returns count."""
    g = graph()
    g.query("""MATCH (f:Fact {id:$id})<-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*1..5]-(x)
               WHERE x.status = 'valid' OR x.status = 'current' SET x.status = 'stale'""", {"id": fact_id})

def repair_queue(fact_id):
    """Tool 5. Ordered repair list: derived facts, then decisions, answers, tasks; each with owner and path proof."""
    items = []
    for n in blast_radius(fact_id):
        d = rows(graph().query(Q_DETAIL, {"id": n["id"]}))[0]
        d.update(id=n["id"], hops=n["hops"])
        d["path"] = path_proof(fact_id, n["id"])
        items.append(d)
    items.sort(key=lambda d: (KIND_ORDER[d["kind"]], d["hops"], d["id"]))
    return items

def mark(node_id, status, verdict=None):
    g = graph()
    g.query("MATCH (x {id:$id}) SET x.status = $s, x.verdict = $v", {"id": node_id, "s": status, "v": verdict or ""})

def unaffected(fact_id):
    """Decisions/Answers/Tasks NOT downstream of the fact (shows the traversal is selective)."""
    hit = {n["id"] for n in blast_radius(fact_id)}
    rs = rows(graph().query("MATCH (x) WHERE x:Decision OR x:Answer OR x:Task RETURN x.id AS id, labels(x)[0] AS kind, coalesce(x.title,x.text) AS label"))
    return [r for r in rs if r["id"] not in hit]

def detail(node_id):
    """Tool 6. One node's kind, label, status, rationale, owner and source document."""
    r = rows(graph().query(Q_DETAIL, {"id": node_id}))
    return r[0] if r else {"error": f"no node with id {node_id}"}
