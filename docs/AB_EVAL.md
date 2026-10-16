# Graph on vs graph off: what the A/B does and does not show

Setup (`python -m aftershock.evalab`): same corpus, same corrected fact (Meridian commission 9% -> 12%), same question
"which decisions, answers and tasks are now stale?". Graph = `blast_radius` traversal. Flat = BM25 over document text, top-k
documents, mapping each retrieved document to the items recorded in it (we give flat that mapping to be generous).

| k (flat) | graph stale-recall | flat stale-recall | false positives (both) |
|---|---|---|---|
| 3 | 11/11 | 0/11 | 0 |
| 6 | 11/11 | 2/11 | 0 |
| 10 | 11/11 | 5/11 | 0 |

What it shows: dependents that never mention the corrected number (a quote that only shows "14%", a billing config, a board margin
target derived from a derived fact) are invisible to text search and reachable by traversal, and the traversal leaves the 5 unrelated items alone.

What it does NOT show: the graph's 11/11 is by construction. The edges are hand-seeded and the ground truth was hand-labelled by the
same author from the same documents, so this is not evidence that edges would be extracted correctly from raw documents
(EmbeddingGemma edge suggestion, see BUILD_LOG.md, is a first, small check of that). Flat has no notion of "items" or "states", so
it is a deliberately plain baseline, not a tuned RAG system. A stronger retriever or an LLM reading more documents would close some of the gap. No benchmark is claimed.
