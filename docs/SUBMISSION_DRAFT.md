# Submission draft (WeMakeDevs panel) - for the user to paste

Track: Company Brain (Track 3). Optional second entry: Track 1 (Agents That Act on Connected Data) - only if time
allows; the plan's cut list drops it first.

## Tagline
Fix one fact. Find everything built on it.

## Description
Companies make decisions on facts, and then the facts change: a draft contract is replaced by the signed one, a number
is corrected. The old fact lives on in decisions, customer quotes, support answers and configs, and nobody can say what
breaks.

Aftershock keeps company knowledge in a FalkorDB graph - facts, decisions, tasks, answers, people and documents, with
provenance and draft/executed document state as first-class data. When a fact is corrected, the agent:

1. Supersedes the old fact (valid_to set, CORRECTED_BY edge - nothing is deleted),
2. Traverses BASED_ON / DERIVED_FROM / IMPLEMENTS edges up to 5 hops to compute the blast radius,
3. Builds a repair queue where every item carries its shortest dependency path as proof, plus its owner,
4. Ranks decisions by downstream dependent count and re-judges the top 3 with an LLM (or flags them for a human),
5. Answers questions either through the graph - an LLM calling live Cypher tools and citing node ids - or, with the
   graph switch off, through flat BM25 document search, so the difference is visible live.

The demo: a synthetic 25-person company priced its product on a 9% marketplace commission from an unsigned draft. The
executed contract says 12%. One click propagates the correction through 13 dependent artifacts.

FalkorDB is the system of record, not a sidecar: every agent step - correction, blast radius, path proofs, re-judge
ranking, Q&A tool calls - is a Cypher query against it.

## Honest scope (include - judges reward it)
The company, its 32 documents and the graph edges are hand-authored seed data; the pipeline that runs on them is real
code. The A/B (graph vs flat search) is run on identical inputs and its limits are stated in the README: the graph's
recall is by construction and no benchmark is claimed.

## Tech
Python, FastAPI, FalkorDB (Cypher), vanilla JS/SVG frontend, BM25 baseline, Gemini/OpenRouter for re-judging and Q&A
(optional; degrades honestly without a key), EmbeddingGemma (edge-suggestion sanity check, not wired in).

## AI use disclosure
Built with AI assistance (an AI agent wrote code and docs under the author's direction). The author reviewed the build
and can explain every part.

## Links
- Repo: (public GitHub link - after push)
- Demo video: docs/demo.mp4 in the repo itself - GitHub plays it inline at
  https://github.com/r0c0y/aftershock/blob/master/docs/demo.mp4 once public (fill in the account after the push).
  Optional upgrade: a YouTube-unlisted upload from his Google account if he prefers; the in-repo link needs nothing extra.
- Local run: docker run -d -p 6379:6379 falkordb/falkordb:latest + pip install -r requirements.txt +
  python -m aftershock.seed + uvicorn aftershock.api:app --port 8000 (details in README)
