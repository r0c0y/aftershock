# Prior art, inputs and credits

Design input from material the author shared during the hackathon week, and what we did with it.

| Source | What it says | What Aftershock does with it |
|---|---|---|
| Dhravya Shah (Supermemory founder) post, shared 13 Oct (screenshot) | Graph DBs for agent memory are hype; no production wins; "temporal fact-based" memory is the better bet | Take the critique seriously. Aftershock does not claim graphs beat vectors at recall. It targets a question flat facts cannot answer: *what is built on this fact?* The graph-off switch makes the contrast live. We also keep time on facts (`valid_to`, `CORRECTED_BY`), which is his temporal point, inside the graph. |
| Harvey, "context graphs" on Legal Agent Bench ([post by @nikogrupen](https://x.com/nikogrupen/status/2110773803592937733), [Harvey LAB article](https://www.harvey.ai/blog/legal-agent-bench-law-firm-knowledge)) | Agent builds a graph of entities, dates, draft vs executed status first; self-reported "up to" 30% better pass rate and ~50% lower cost; flat search picked the wrong precedent | Borrowed the idea of **document state** (draft / executed / superseded) as first-class data and the wrong-precedent failure story. We do NOT claim their numbers or run a benchmark. |
| Clueso (clueso.io) | Product videos go stale when the UI changes; it re-records demos on every release | Same pain, different object: company knowledge rots the same way. Aftershock is "re-record on change" for facts and decisions. |
| EmbeddingGemma | Open, local embeddings | Role: suggest candidate edges between new and existing nodes, for human/agent confirmation. A standalone script (`suggest_edges.py`) runs it on CPU and ranks the seeded fact in the top 2 for 9 of 9 decision/answer edges (caveats in BUILD_LOG.md). NOT wired into the live product. |
| Graphiti (getzep) | Bi-temporal facts: invalidate, don't delete | Borrowed the supersede-instead-of-delete idea; implemented in plain Cypher (`valid_to`, `CORRECTED_BY`). |
| HelixDB helix-foundry | Local-first workspace connecting company data into one ontology | Prior art for "company brain on a graph". Differentiator: they build the ontology; we repair decisions when a fact changes. |
| ihatefiles.com | File converter competitor to another project | Not related to this project; not used. |

Not recovered: the contents of X posts by @StanleyWei4748, @hudson_gri, @sarahfim and @realAkashAnand could not be fetched (X blocks automated reads), so nothing here is derived from them.
