"""A/B on identical inputs: same corpus, same corrected fact (9% -> 12%). Question: which items are stale?
GRAPH: blast_radius traversal. FLAT: BM25 over document text (top-k docs), items = those recorded in a retrieved doc.
Ground truth is hand-labelled by the author from the documents (seeded, not independent). Run: python -m aftershock.evalab"""
from .seed import seed
from . import tools as T
from .flat import Flat
from .db import graph, rows

# Items that truly relied on the 9% figure, labelled by reading corpus/documents (not by running the graph).
TRUTH = {"d-price-49", "d-partnerfee-14", "d-halden-disc", "d-margin-target", "a-halden-quote", "a-brightwater-quote",
         "a-orla-quote", "a-faq-fee", "t-pricing-page", "t-billing-config", "t-halden-send"}
QUERY = "Meridian marketplace commission 9%"

def item_docs():
    r = rows(graph().query("MATCH (x)-[:RECORDED_IN]->(d:Document) RETURN x.id AS id, d.id AS doc"))
    return {x["id"]: x["doc"] for x in r}

def score(found, name):
    tp = len(found & TRUTH); fp = len(found - TRUTH)
    print(f"{name:14s} found {len(found):2d}  stale-recall {tp}/{len(TRUTH)}  false positives {fp}")
    return tp, fp

def main(k=6):
    seed()
    docs = item_docs()
    graph_found = {n["id"] for n in T.blast_radius("f-comm-9") if n["kind"] != "Fact"}
    flat = Flat()
    hits = flat.search(QUERY, k=k)
    print("flat top docs:", [(h["id"], h["state"]) for h in hits])
    flat_found = {i for i, d in docs.items() if d in {h["id"] for h in hits}}
    score(graph_found, "graph"); score(flat_found, f"flat(top{k})")
    print("missed by flat:", sorted(TRUTH - flat_found))
    print("flat docs that are NOT about the fact:", [h["id"] for h in hits if h["id"] in ("doc-24", "doc-28", "doc-21")])

if __name__ == "__main__":
    main()
