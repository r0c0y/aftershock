"""Graph-on Q&A: the LLM answers by calling the real graph tools, never from memory.

The loop: the model sees the question plus the running tool results and replies with JSON -
either {"tool": <name>, "args": {...}} to call a tool, or {"answer": ...} to finish.
Every tool runs a real Cypher query against FalkorDB. Called only when an API key is set;
without one the API falls back to an extractive answer, labelled as such. We never invent
an answer the tools did not support.
"""
import json
from . import tools as T
from .llm import complete_json, provider

MAX_CALLS = 4

def search_facts(keyword):
    kws = [w for w in keyword.lower().split() if len(w) > 2]
    out = []
    for f in T.current_facts():
        hits = sum(1 for k in kws if k in f["text"].lower())
        if hits:
            out.append({"id": f["id"], "text": f["text"], "status": f["status"], "hits": hits})
    return sorted(out, key=lambda f: -f["hits"])[:5]

TOOLKIT = {
    "current_facts": ("no args - list every fact with its status (current / superseded / stale)",
                      lambda a: T.current_facts()),
    "search_facts": ('args {"keyword": "..."} - keyword search over fact texts, returns matching facts with status',
                     lambda a: search_facts(a.get("keyword", ""))),
    "blast_radius": ('args {"fact_id": "..."} - every Fact/Decision/Answer/Task downstream of the fact, with hop counts',
                     lambda a: T.blast_radius(a["fact_id"])),
    "path_proof": ('args {"fact_id": "...", "node_id": "..."} - exact dependency path from the node back to the fact, plus the documents the fact was stated in',
                   lambda a: T.path_proof(a["fact_id"], a["node_id"])),
    "node_detail": ('args {"node_id": "..."} - kind, label, status, rationale, owner and source document for any node',
                    lambda a: T.detail(a["node_id"])),
}

SYS = """You answer questions about a company using ONLY its knowledge graph. You may call these tools (each runs a live Cypher query against FalkorDB):
%s

Reply with JSON only, one of:
  {"tool": "<name>", "args": {...}}  to call a tool (at most %d tool calls in total)
  {"answer": "<2-4 sentences>"}      when you can answer

Rules: never state a number or name that did not appear in a tool result. Cite node ids (like f-comm-9) for every claim. Say when a fact you rely on is superseded or stale. If the tools cannot answer the question, answer with exactly that."""

def answer(question):
    """Returns {"answer", "calls", "by"}. Raises LLMUnavailable when no key / the call fails."""
    calls = []
    sys = SYS % ("\n".join(f"- {name}: {desc}" for name, (desc, _) in TOOLKIT.items()), MAX_CALLS)
    for _ in range(MAX_CALLS + 1):
        transcript = "\n".join(
            f"call {i + 1}: {c['tool']}({json.dumps(c['args'])}) -> {json.dumps(c['result'])[:1500]}"
            for i, c in enumerate(calls))
        prompt = f"Question: {question}\n\nTool results so far:\n{transcript or '(none yet)'}"
        try:
            v = complete_json(sys, prompt)
        except (ValueError, AttributeError, KeyError):
            break  # model did not return usable JSON; stop honestly with the trace we have
        if isinstance(v, dict) and "answer" in v:
            return {"answer": v["answer"], "by": provider(),
                    "calls": [{"tool": c["tool"], "args": c["args"]} for c in calls]}
        name, args = (v.get("tool"), v.get("args") or {}) if isinstance(v, dict) else (None, {})
        if name not in TOOLKIT:
            calls.append({"tool": str(name), "args": args, "result": {"error": "unknown tool"}})
            continue
        try:
            res = TOOLKIT[name][1](args)
        except Exception as e:
            res = {"error": f"{type(e).__name__}: {e}"}
        calls.append({"tool": name, "args": args, "result": res})
    return {"answer": f"Stopped after {len(calls)} tool call(s) without a final answer; the trace shows what was checked.",
            "by": provider(), "calls": [{"tool": c["tool"], "args": c["args"]} for c in calls]}
