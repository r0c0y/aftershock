"""Load the synthetic company into FalkorDB. Run: python -m aftershock.seed"""
import glob, os, re, time
from .db import graph, GRAPH
from . import seed_data as S

DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus", "documents")
NOW = "2026-10-16"

def load_documents():
    docs = []
    for p in sorted(glob.glob(os.path.join(DOC_DIR, "*.md"))):
        raw = open(p).read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        meta = dict(l.split(": ", 1) for l in m.group(1).splitlines())
        meta["body"] = m.group(2).strip()
        docs.append(meta)
    return docs

def seed(reset=True):
    g = graph()
    if reset:
        try: g.delete()
        except Exception: pass
        g = graph()
    for q in ["CREATE INDEX FOR (n:Fact) ON (n.id)", "CREATE INDEX FOR (n:Document) ON (n.id)",
              "CREATE INDEX FOR (n:Decision) ON (n.id)", "CREATE INDEX FOR (n:Answer) ON (n.id)",
              "CREATE INDEX FOR (n:Task) ON (n.id)", "CREATE INDEX FOR (n:Person) ON (n.id)",
              "CREATE INDEX FOR (n:Project) ON (n.id)"]:
        g.query(q)
    for d in load_documents():
        g.query("CREATE (:Document {id:$id,title:$title,state:$state,date:$date,author:$author,kind:$kind,body:$body})", d)
    for pid, name, role in S.PEOPLE:
        g.query("CREATE (:Person {id:$id,name:$n,role:$r})", {"id": pid, "n": name, "r": role})
    for prid, name in S.PROJECTS:
        g.query("CREATE (:Project {id:$id,name:$n})", {"id": prid, "n": name})
    for fid, text, docs in S.FACTS:
        g.query("CREATE (:Fact {id:$id,text:$t,status:'current',valid_from:'2026-07-20',valid_to:''})", {"id": fid, "t": text})
        for d in docs:
            g.query("MATCH (f:Fact {id:$f}),(d:Document {id:$d}) CREATE (f)-[:STATED_IN]->(d)", {"f": fid, "d": d})
    for c, p in S.FACT_DERIVED_FROM:
        g.query("MATCH (a:Fact {id:$c}),(b:Fact {id:$p}) CREATE (a)-[:DERIVED_FROM]->(b)", {"c": c, "p": p})
    for did, title, why, owner, proj, src, facts in S.DECISIONS:
        g.query("CREATE (:Decision {id:$id,title:$t,rationale:$r,status:'valid',made_at:'2026-08-04'})", {"id": did, "t": title, "r": why})
        g.query("MATCH (p:Person {id:$o}),(x:Decision {id:$i}) CREATE (p)-[:OWNS]->(x)", {"o": owner, "i": did})
        g.query("MATCH (p:Project {id:$o}),(x:Decision {id:$i}) CREATE (x)-[:PART_OF]->(p)", {"o": proj, "i": did})
        g.query("MATCH (d:Document {id:$o}),(x:Decision {id:$i}) CREATE (x)-[:RECORDED_IN]->(d)", {"o": src, "i": did})
        for f in facts:
            g.query("MATCH (a:Decision {id:$i}),(f:Fact {id:$f}) CREATE (a)-[:BASED_ON]->(f)", {"i": did, "f": f})
    for aid, text, src, deps in S.ANSWERS:
        g.query("CREATE (:Answer {id:$id,text:$t,status:'valid'})", {"id": aid, "t": text})
        g.query("MATCH (d:Document {id:$o}),(x:Answer {id:$i}) CREATE (x)-[:RECORDED_IN]->(d)", {"o": src, "i": aid})
        for dep in deps:
            g.query("MATCH (a:Answer {id:$i}),(n {id:$d}) WHERE n:Decision OR n:Fact CREATE (a)-[:DERIVED_FROM]->(n)", {"i": aid, "d": dep})
    for tid, title, state, owner, dec, src in S.TASKS:
        g.query("CREATE (:Task {id:$id,title:$t,state:$s,status:'valid'})", {"id": tid, "t": title, "s": state})
        g.query("MATCH (p:Person {id:$o}),(x:Task {id:$i}) CREATE (p)-[:OWNS]->(x)", {"o": owner, "i": tid})
        g.query("MATCH (a:Task {id:$i}),(d:Decision {id:$d}) CREATE (a)-[:IMPLEMENTS]->(d)", {"i": tid, "d": dec})
        g.query("MATCH (d:Document {id:$o}),(x:Task {id:$i}) CREATE (x)-[:RECORDED_IN]->(d)", {"o": src, "i": tid})
    for new, old in S.SUPERSEDES:
        g.query("MATCH (a:Document {id:$n}),(b:Document {id:$o}) CREATE (a)-[:SUPERSEDES]->(b)", {"n": new, "o": old})
    return g

if __name__ == "__main__":
    g = seed()
    for label in ["Document", "Fact", "Decision", "Answer", "Task", "Person", "Project"]:
        n = g.query(f"MATCH (n:{label}) RETURN count(n)").result_set[0][0]
        print(f"{label:9s} {n}")
    print("edges", g.query("MATCH ()-[r]->() RETURN count(r)").result_set[0][0])
