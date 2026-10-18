# Aftershock

**Fix one fact. Find everything built on it.**

Companies make decisions on facts, then the facts change: a draft contract gets replaced by the signed one, a number is
corrected. The old fact lives on in decisions, customer quotes, support answers and tickets. Aftershock keeps company
knowledge in a FalkorDB graph, and when a fact is corrected it traverses the graph to find the **blast radius**, builds a
**repair queue** where every item carries its **graph path as proof**, and re-judges the highest-impact decisions.

Built for [Graph Hacks (WeMakeDevs x FalkorDB)](https://www.wemakedevs.org/hackathons/falkordb), Company Brain track
("tracing decisions back to their source", "keeping knowledge current as things change").

## Demo
**[docs/demo.mp4](./docs/demo.mp4)** (2:18) - a real usage recording: both questions typed live, the graph on/off
switch, the correction, the repair queue and an evidence path. Recorded without an LLM key, so re-judging shows
`needs_human` honestly instead of a faked verdict; with `GEMINI_API_KEY` or `OPENROUTER_API_KEY` set, the same run
produces real LLM verdicts and tool-calling Q&A.

> STATUS: work in progress, private repo. Build log is in `docs/BUILD_LOG.md`.

## The demo in one scene
Larkspur Supply (synthetic, 25 people) priced its Pro plan assuming Meridian marketplace takes **9%** (an unsigned draft).
The executed contract says **12%**. Click *Apply correction*:

1. `correct_fact` supersedes the 9% fact (`valid_to` set, `CORRECTED_BY` edge, nothing deleted).
2. `blast_radius` traverses `BASED_ON | DERIVED_FROM | IMPLEMENTS` up to 5 hops: 13 nodes flagged, 5 unrelated ones untouched.
3. The repair queue lists derived facts, decisions, answers and tasks, each with owner and shortest-path evidence chain.
4. The 3 decisions with the most downstream dependents are re-judged by an LLM.
5. The **Graph switch** turns the graph off: the same question answered by flat BM25 retrieval over document text.

## Ask the company (graph on vs off)
The Ask box answers the same question two ways:

* **Graph on**: with an API key set, the LLM answers by *calling the graph tools* (`search_facts`, `blast_radius`,
  `path_proof`, `node_detail`, `current_facts`) and may only use what those live Cypher queries return; the UI lists the
  exact tool calls it made. Without a key it falls back to a labelled extractive answer from the same Cypher queries.
  Try the multi-hop question: *"Who owns the tasks affected by the Meridian commission change?"* - a Fact -> Decision ->
  Task -> Person traversal (graph-on names Elena, Tom, Maya, Aisha and Leo with their items).
* **Graph off**: flat BM25 over the document text. No edges, no states, no owners. On the multi-hop question its top hit
  is the *unsigned draft* contract and it cannot name a single owner.

## What the A/B does and does not show
Full write-up in `docs/AB_EVAL.md`. Plainly: the graph side's 11/11 stale-item recall is **by construction** - the edges
are hand-seeded and the ground truth was hand-labelled by the same author, so the A/B is *not* evidence that edges would
be extracted correctly from raw documents. The flat side is a deliberately plain BM25 baseline, not a tuned RAG system.
What the A/B does show, live in the UI: dependents that never mention the corrected number (a billing config, a board
margin target) are invisible to text search and reachable by traversal, and the traversal leaves the 5 unrelated items
alone. No benchmark is claimed.

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

Optional: the **Suggest edges** button runs EmbeddingGemma-300m locally (ONNX int8, CPU) to propose candidate edges
(dotted, unconfirmed, never written to the graph). It needs the model files, which are not in the repo:
`huggingface-cli download onnx-community/embeddinggemma-300m-ONNX --local-dir models/embeddinggemma` (~315 MB).

## Docs
`docs/GRAPH_MODEL.md` schema and the Cypher for every tool · `docs/ARCHITECTURE.md` components and request flows ·
`docs/DECISIONS.md` key design decisions · `docs/AB_EVAL.md` the graph on/off evaluation · `docs/REAL_VS_SEEDED.md` ·
`docs/INSPIRATION.md` prior art and credits · `docs/DEV_ENVIRONMENT.md` · `docs/BUILD_LOG.md`.

## AI use disclosure
Built with AI assistance (an AI agent wrote code and docs under the author's direction). Runtime LLM: Gemini / OpenRouter for re-judging and answers.
