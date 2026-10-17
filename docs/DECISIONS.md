# Key design decisions

1. **Supersede, never delete.** A correction writes a new Fact and a `CORRECTED_BY` edge and sets `valid_to` on the old
   one. The stale chain stays inspectable, which is the whole point of the audit story. Borrowed from Graphiti's
   bi-temporal model, implemented in plain Cypher.
2. **Document state is first-class.** Every document is draft / executed / superseded (Harvey-style). The demo failure -
   pricing built on an unsigned draft - only exists because state is data, not prose. `correct_fact` flips the source
   document to `executed`.
3. **The graph decides the re-judge order.** Re-judging is capped at 3 decisions, ranked by the number of downstream
   dependents (a Cypher count, not an LLM guess). An LLM with a fixed budget spends it where the graph says impact is.
4. **No key, no fake.** Without GEMINI_API_KEY / OPENROUTER_API_KEY every LLM step degrades to a labelled honest state:
   re-judging says `needs_human`, Q&A says `answered by: none (extractive)`. The demo works end to end without a key.
5. **LLM answers only from tool results.** In graph-on Q&A the model must call the Cypher tools and cite node ids; the
   system prompt forbids numbers or names that did not appear in a tool result. The UI shows the exact calls made.
6. **The flat baseline is deliberately plain.** BM25 over document text, no chunking tricks, no reranker - because the
   claim is "some questions need edges", not "we beat tuned RAG". Stated in docs/AB_EVAL.md.
7. **Seeded corpus, real pipeline.** 32 hand-authored documents and hand-authored edges (disclosed in
   docs/REAL_VS_SEEDED.md). Extraction from raw documents is future work; EmbeddingGemma edge suggestion is a first,
   small sanity check of that direction and is not claimed as more.
8. **Layered-column UI.** Facts -> Decisions -> Tasks -> Answers left to right, so the blast radius reads as waves from
   one node. Red ring = stale, grey dashed = superseded, amber = re-judged and changed.
