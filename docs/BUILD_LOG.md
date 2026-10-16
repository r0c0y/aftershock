# Build log

## Fri 16 Oct, ~17:55 IST - piece 1 and EmbeddingGemma check
- Corpus (32 docs), graph seed, FalkorDB tools, FastAPI + UI, 2 tests. Correction flags 13 nodes, leaves 5 untouched.
- EmbeddingGemma-300m (ONNX int8 mirror, CPU, ~0.3 s per batch) suggests Fact candidates per Decision/Answer.
  Measured on our own seed: it ranks the seeded fact in its top 2 for 9 of 9 decision/answer->fact edges. Caveats: tiny
  set (11 items, 8 facts), seed edges were authored by us knowing the text, 2 of 11 items had no direct fact edge but still got
  2 suggestions (precision is not claimed). This is a sanity check, not a benchmark. Role in product: suggest edges for human/agent confirmation.
- No LLM key yet: re-judging reports needs_human.
