# Aftershock

**Fix one fact. Find everything built on it.**

Companies make decisions on facts, then the facts change: a draft contract gets replaced by the signed one, a number is
corrected. The old fact lives on in decisions, customer quotes, support answers and tickets. Aftershock keeps company
knowledge in a FalkorDB graph, and when a fact is corrected it traverses the graph to find the **blast radius**, builds a
**repair queue** where every item carries its **graph path as proof**, and re-judges the highest-impact decisions.

Built for [Graph Hacks (WeMakeDevs x FalkorDB)](https://www.wemakedevs.org/hackathons/falkordb), Company Brain track
("tracing decisions back to their source", "keeping knowledge current as things change").

> STATUS: work in progress, private repo. Build log is in `docs/BUILD_LOG.md`.

## The demo in one scene
Larkspur Supply (synthetic, 25 people) priced its Pro plan assuming Meridian marketplace takes **9%** (an unsigned draft).
The executed contract says **12%**. Click *Apply correction*:

1. `correct_fact` supersedes the 9% fact (`valid_to` set, `CORRECTED_BY` edge, nothing deleted).
2. `blast_radius` traverses `BASED_ON | DERIVED_FROM | IMPLEMENTS` up to 5 hops: 13 nodes flagged, 5 unrelated ones untouched.
3. The repair queue lists derived facts, decisions, answers and tasks, each with owner and shortest-path evidence chain.
4. The 3 decisions with the most downstream dependents are re-judged by an LLM.
5. The **Graph switch** turns the graph off: the same question answered by flat BM25 retrieval over document text.

## Real vs seeded (read this)
See `docs/REAL_VS_SEEDED.md`. Short version: the company, its 32 documents and the graph edges are **hand-authored seed data**.
FalkorDB, the traversal, correction semantics, path proofs, repair queue, re-judging and the flat baseline are **real code**.
No benchmark numbers are claimed.

## Run it
```
docker run -d -p 6379:6379 falkordb/falkordb:latest
pip install -r requirements.txt
python -m aftershock.seed                      # loads the synthetic company
export GEMINI_API_KEY=...                      # or OPENROUTER_API_KEY; without a key re-judging says "needs human"
uvicorn aftershock.api:app --port 8000         # open http://localhost:8000
python -m pytest tests
```

## Docs
`docs/GRAPH_MODEL.md` schema and the Cypher for every tool · `docs/ARCHITECTURE.md` · `docs/DECISIONS.md` key design decisions ·
`docs/REAL_VS_SEEDED.md` · `docs/INSPIRATION.md` prior art and credits · `docs/DEV_ENVIRONMENT.md`.

## AI use disclosure
Built with AI assistance (an AI agent wrote code and docs under the author's direction). Runtime LLM: Gemini / OpenRouter for re-judging and answers.
