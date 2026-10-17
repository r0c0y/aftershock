"""EmbeddingGemma edge suggestion: for every Decision/Answer, rank Facts by cosine similarity.
Reports how many suggestions match the hand-authored (seeded) edges. Run: python -m aftershock.suggest_edges"""
import numpy as np
from . import seed_data as S
from .embed import embed

def run(k=2):
    facts = [(f[0], f[1]) for f in S.FACTS]
    F = embed([t for _, t in facts])
    items = [(d[0], d[1] + ". " + d[2], set(x for x in d[6])) for d in S.DECISIONS] + \
            [(a[0], a[1], set(x for x in a[3] if x.startswith("f-"))) for a in S.ANSWERS]
    # answers also depend on decisions; compare only the fact edges they carry directly
    hit = tot = sug = 0; rows_ = []
    for iid, text, truth in items:
        q = embed([text], "query")[0]
        sims = F @ q
        top = [facts[i][0] for i in np.argsort(-sims)[:k]]
        if truth:
            tot += len(truth); hit += len(truth & set(top))
        sug += len(top); rows_.append((iid, top, sorted(truth)))
    return rows_, hit, tot, sug

if __name__ == "__main__":
    r, hit, tot, sug = run()
    for x in r: print(x)
    print(f"seeded fact-edges recovered in top-2: {hit}/{tot}")

def suggest_live(k=2):
    """Same idea, but over the LIVE graph: for each Decision/Answer, rank Facts by cosine and
    return candidate edges that do not already exist. Raises OSError if the model is not downloaded."""
    from .db import graph, rows
    g = graph()
    facts = rows(g.query("MATCH (f:Fact) RETURN f.id AS id, f.text AS text"))
    items = rows(g.query("MATCH (x) WHERE x:Decision OR x:Answer RETURN x.id AS id, coalesce(x.title, x.text) AS text"))
    ex = {(r["s"], r["d"]) for r in rows(g.query("MATCH (x)-[:BASED_ON|DERIVED_FROM]->(f:Fact) RETURN x.id AS s, f.id AS d"))}
    F = embed([f["text"] for f in facts])
    out = []
    for it in items:
        q = embed([it["text"]], "query")[0]
        sims = F @ q
        for i in np.argsort(-sims)[:k]:
            fid = facts[int(i)]["id"]
            if (it["id"], fid) not in ex:
                out.append({"src": it["id"], "dst": fid, "score": round(float(sims[int(i)]), 3)})
    return out
