# Real vs seeded

| Piece | Status |
|---|---|
| Company, people, 32 documents (`corpus/documents`) | **Seeded**, synthetic, hand-written |
| Facts, decisions, answers, tasks and their edges (`aftershock/seed_data.py`) | **Seeded**, hand-authored to match the documents (not LLM-extracted) |
| FalkorDB graph, indexes, Cypher | **Real** (FalkorDB 4.22.1 from the official `falkordb/falkordb` image) |
| correct_fact, blast radius, path proofs, repair queue, stale flagging | **Real** code and queries |
| Re-judging | **Real** LLM call; with no API key the item is marked `needs_human`, never invented |
| Flat baseline (BM25) | **Real**, deliberately simple; it is the "graph off" comparison, not a tuned retriever |
| Benchmarks | **None claimed** |
