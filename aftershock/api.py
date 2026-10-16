import os, re
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from . import agent, tools as T, seed_data as S
from .db import graph, rows
from .flat import Flat, tok
from .llm import complete, provider, LLMUnavailable
from .seed import seed

app = FastAPI(title="Aftershock")
WEB = os.path.join(os.path.dirname(__file__), "..", "web")
FLAT = Flat()
STATE = {"corrected": False, "last": None}

@app.get("/")
def index():
    return FileResponse(os.path.join(WEB, "index.html"))

@app.get("/api/status")
def status():
    g = graph()
    return {"corrected": STATE["corrected"], "llm": provider() or "none",
            "counts": {k: g.query(f"MATCH (n:{k}) RETURN count(n)").result_set[0][0] for k in ["Document", "Fact", "Decision", "Answer", "Task"]}}

@app.get("/api/graph")
def graph_view():
    g = graph()
    nodes = rows(g.query("MATCH (n) WHERE n:Fact OR n:Decision OR n:Answer OR n:Task RETURN n.id AS id, labels(n)[0] AS kind, coalesce(n.title,n.text) AS label, n.status AS status"))
    edges = rows(g.query("MATCH (a)-[r:BASED_ON|DERIVED_FROM|IMPLEMENTS|CORRECTED_BY]->(b) RETURN a.id AS src, b.id AS dst, type(r) AS type"))
    return {"nodes": nodes, "edges": edges}

@app.post("/api/reset")
def reset():
    seed(); STATE.update(corrected=False, last=None)
    return {"ok": True}

@app.post("/api/correct")
def correct(rejudge: bool = True):
    if STATE["corrected"]:
        return JSONResponse({"error": "already corrected; reset first"}, 409)
    events = []
    result = agent.run(emit=events.append, do_rejudge=rejudge)
    STATE.update(corrected=True, last=result)
    return {"events": events, **result}

def _kw(q):
    return [w for w in tok(q) if len(w) > 2 and w not in {"what", "which", "how", "much", "does", "our", "we", "do", "pay", "take", "sales", "company"}]

@app.get("/api/ask")
def ask(q: str, graph_on: bool = True):
    if not graph_on:
        hits = FLAT.search(q, k=3)
        ctx = "\n\n".join(f"[{h['id']} | {h['title']}]\n{h['body']}" for h in hits)
        out = {"mode": "flat (BM25 over document text only; no edges, no states, no corrections)", "retrieved": [{k: h[k] for k in ("id", "title", "score")} for h in hits]}
        try:
            out["answer"] = complete("Answer from the documents only, briefly. Cite doc ids.", f"Documents:\n{ctx}\n\nQuestion: {q}")
            out["answer_by"] = provider()
        except LLMUnavailable as e:
            out["answer"] = f"(no LLM configured; top retrieved passage: {hits[0]['body'][:240]}...)"; out["answer_by"] = "none"
        return out
    kws = _kw(q)
    g = graph()
    facts = rows(g.query("MATCH (f:Fact) WHERE f.status = 'current' "
                         "WITH f, size([k IN $kws WHERE toLower(f.text) CONTAINS k]) AS hits WHERE hits > 0 "
                         "OPTIONAL MATCH (f)-[:STATED_IN]->(d:Document) "
                         "RETURN f.id AS id, f.text AS text, hits, collect(d.id + ' (' + d.state + ')') AS sources ORDER BY hits DESC LIMIT 2", {"kws": kws}))
    dependents = {f["id"]: [(n["id"], n["kind"]) for n in T.blast_radius(f["id"])] for f in facts}
    out = {"mode": "graph (Cypher: current facts only, provenance edges, dependents)", "facts": facts, "dependents": dependents}
    ctx = "\n".join(f"- {f['id']}: {f['text']} (stated in {', '.join(f['sources'])})" for f in facts)
    try:
        out["answer"] = complete("Answer from the graph facts only, briefly. Cite fact ids and source docs.", f"Current facts from the knowledge graph:\n{ctx}\n\nQuestion: {q}")
        out["answer_by"] = provider()
    except LLMUnavailable:
        out["answer"] = "Current graph facts: " + "; ".join(f"{f['text']} [{f['id']}]" for f in facts); out["answer_by"] = "none (extractive)"
    return out

app.mount("/static", StaticFiles(directory=WEB), name="static")
