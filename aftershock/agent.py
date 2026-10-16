"""Aftershock pipeline: correction -> blast radius -> repair queue -> re-judge (max 3)."""
from . import tools as T, seed_data as S
from .db import graph, rows
from .llm import complete_json, LLMUnavailable

MAX_REJUDGE = 3

JUDGE_SYS = ("You audit company decisions after a supporting fact is corrected. Reply with JSON only: "
             '{"still_valid": bool, "reasoning": str (max 2 sentences), "proposed_change": str (concrete, or "none")}. '
             "Use only the facts provided; do not invent numbers you were not given.")

Q_IMPACT = """
MATCH (d:Decision {id:$id})
OPTIONAL MATCH (x)-[:IMPLEMENTS|DERIVED_FROM*1..3]->(d)
RETURN count(DISTINCT x) AS dependents"""

def rank_for_rejudge(queue):
    """Graph decides what to re-judge first: Decisions with the most downstream dependents."""
    out = []
    for it in queue:
        if it["kind"] == "Decision":
            n = rows(graph().query(Q_IMPACT, {"id": it["id"]}))[0]["dependents"]
            out.append((n, it))
    out.sort(key=lambda x: (-x[0], x[1]["hops"], x[1]["id"]))
    return [(n, it) for n, it in out]

def rejudge(item, old, new, evidence):
    """Real LLM call. If no key / call fails, the item is marked needs_human, never invented."""
    prompt = (f"Decision: {item['label']}\nRationale recorded at the time: {item['rationale']}\n"
              f"Fact it relied on (now SUPERSEDED): {old['text']}\nCorrected fact (current): {new['text']}\n"
              f"Correction evidence: {evidence}\nIs the decision still valid? If not, what concrete change is needed?")
    try:
        v = complete_json(JUDGE_SYS, prompt)
        return {"status": "rejudged_ok" if v.get("still_valid") else "rejudged_changed", **v}
    except LLMUnavailable as e:
        return {"status": "needs_human", "still_valid": None, "reasoning": f"LLM unavailable ({e}). Flagged for human re-judgment.", "proposed_change": "none"}

def run(correction=S.CORRECTION, emit=print, do_rejudge=True):
    """Returns a dict the UI renders. `emit` receives step events (the visible agent trace)."""
    old = T.get_fact(correction["old_fact"])
    emit({"step": "correct_fact", "msg": f"Superseding {old['id']}: \"{old['text']}\""})
    res = T.correct_fact(correction["old_fact"], correction["new_fact_id"], correction["new_text"], correction["source_doc"], correction["note"])
    new = T.get_fact(correction["new_fact_id"])
    emit({"step": "corrected", "msg": f"New fact {new['id']}: \"{new['text']}\" (CORRECTED_BY edge written, nothing deleted)"})
    rad = T.blast_radius(old["id"])
    emit({"step": "blast_radius", "msg": f"Traversal found {len(rad)} dependent nodes (max {max(r['hops'] for r in rad)} hops)", "count": len(rad)})
    T.flag_stale(old["id"])
    queue = T.repair_queue(old["id"])
    emit({"step": "repair_queue", "msg": f"Repair queue built: {len(queue)} items, each with a graph path"})
    ranked = rank_for_rejudge(queue)
    judged = {}
    if do_rejudge:
        for n, it in ranked[:MAX_REJUDGE]:
            emit({"step": "rejudge", "msg": f"Re-judging {it['id']} ({n} dependents downstream)"})
            v = rejudge(it, old, new, correction["note"])
            T.mark(it["id"], v["status"], v.get("proposed_change"))
            judged[it["id"]] = v
            emit({"step": "verdict", "msg": f"{it['id']}: {v['status']}", "verdict": v})
    for it in queue:
        it["verdict"] = judged.get(it["id"])
        it["status"] = (judged.get(it["id"]) or {}).get("status", "stale")
    return {"old": old, "new": new, "queue": queue, "unaffected": T.unaffected(old["id"]), "judged": judged}
