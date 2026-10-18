# Build log

## Fri 16 Oct, ~17:55 IST - piece 1 and EmbeddingGemma check
- Corpus (32 docs), graph seed, FalkorDB tools, FastAPI + UI, 2 tests. Correction flags 13 nodes, leaves 5 untouched.
- EmbeddingGemma-300m (ONNX int8 mirror, CPU, ~0.3 s per batch) suggests Fact candidates per Decision/Answer.
  Measured on our own seed: it ranks the seeded fact in its top 2 for 9 of 9 decision/answer->fact edges. Caveats: tiny
  set (11 items, 8 facts), seed edges were authored by us knowing the text, 2 of 11 items had no direct fact edge but still got
  2 suggestions (precision is not claimed). This is a sanity check, not a benchmark. Role in product: suggest edges for human/agent confirmation.
- No LLM key yet: re-judging reports needs_human.

## Sat 17 Oct, ~15:20 IST - multi-hop Q&A and tool-calling loop
- `qa.py`: graph-on Ask is now an LLM tool-calling loop. The model picks from 5 tools (current_facts, search_facts,
  blast_radius, path_proof, node_detail - each a live Cypher query), may call up to 4, and must answer only from tool
  results with node-id citations. UNTESTED against a real LLM: still no API key (vault approval pending), so this loop
  has only been syntax- and fallback-tested. Will be verified or honestly reported when a key lands.
- Extractive (no-key) fallback now answers multi-hop questions: "Who owns the tasks affected by the Meridian commission
  change?" returns 4 decisions + 3 tasks with real owners via traversal. Graph-off on the same question retrieves the
  unsigned draft contract and names no owner.
- `tools.detail` added (one node: kind, label, status, rationale, owner, source doc). Tests: 2 -> 4, all passing.
- Docs: README now states plainly what the A/B does and does not show; ARCHITECTURE.md and DECISIONS.md added;
  INSPIRATION.md EmbeddingGemma row corrected (script exists, not wired into the product).

## Sat 17 Oct, ~15:25 IST - EmbeddingGemma wired into the UI, setup fixes
- "Suggest edges" button: EmbeddingGemma-300m ranks candidate Decision/Answer -> Fact edges over the LIVE graph
  (top-2 per item, existing edges excluded), drawn dotted and labelled unconfirmed; never written to the graph.
  14 candidates on the seed. Endpoint returns 503 with instructions if the model files are missing.
- Fixed requirements.txt (listed a nonexistent `embeddinggemma` package; real deps are onnxruntime, tokenizers, numpy).
- README: model download instructions (models/ is gitignored); scripts/dev_up.sh bring-up script.

## Sun 18 Oct, ~09:10 IST - demo video recorded (no-key fallback)
- No vault approval overnight: the demo runs in its honest no-key mode (re-judge = needs_human, disclosed on camera).
- Demo video recorded: 2:22, 1280x720 mp4, captioned scenes per docs/VIDEO_SCRIPT.md (flat-search fail on the draft,
  correction + blast radius + repair queue + evidence path, multi-hop owner question graph-on vs graph-off, close).
- Voiceover: captions carry the narration; the user can record his own voice per VIDEO_SCRIPT.md, or request a TTS
  voiceover from the main agent (speak is main-only).
- Infra note: uvicorn was OOM-killed mid-first-attempt (2 GB sandbox + Chrome); dev_up.sh recovered; second attempt
  at 720p succeeded. Video file is NOT in the repo (2 MB deliverable, handed to the user directly).
