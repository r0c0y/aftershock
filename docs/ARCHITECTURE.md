# Architecture

One FalkorDB graph is the system of record; everything else reads or writes it through Cypher.

```
corpus/documents/*.md --(seed.py)--> FalkorDB :6379
seed_data.py (hand-authored nodes/edges) --^
                                            |
web/index.html --HTTP--> api.py (FastAPI) --+--> tools.py   (6 graph tools, each one Cypher query)
                        |                   +--> agent.py   (correction pipeline: correct -> blast radius -> queue -> re-judge)
                        |                   +--> qa.py      (LLM tool-calling Q&A loop, graph-on mode)
                        |                   +--> flat.py    (BM25 baseline, document text only, graph-off mode)
                        +--> llm.py (Gemini REST, OpenRouter fallback; no key = LLMUnavailable, never faked)

embed.py + suggest_edges.py: EmbeddingGemma-300m (ONNX int8, CPU) ranks candidate edges. Standalone sanity check,
not wired into the live pipeline. evalab.py: the graph on/off A/B.
```

Request flows:

* **Apply correction** (`POST /api/correct`): `agent.run` -> `correct_fact` (supersede, write `CORRECTED_BY`) ->
  `blast_radius` (variable-length traversal, 1..5 hops) -> `flag_stale` -> `repair_queue` (each item with a shortest-path
  proof and owner) -> re-judge the top 3 decisions by downstream-dependent count (LLM verdict, or `needs_human`).
* **Ask, graph on**: `qa.answer` loops up to 4 LLM-chosen tool calls, each a live Cypher query; the answer must cite node
  ids from tool results. No key: labelled extractive answer from the same queries.
* **Ask, graph off**: `Flat.search` BM25 top-3 documents; with a key the LLM answers from those passages only.

State outside the graph: `STATE` dict in api.py (corrected flag, last run) and the UI toggle. Nothing else.
