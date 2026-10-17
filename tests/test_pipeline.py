"""Run: python -m pytest tests  (needs FalkorDB on localhost:6379)"""
from aftershock.seed import seed
from aftershock import agent, tools as T

def test_blast_radius_is_selective():
    seed()
    rad = {n["id"] for n in T.blast_radius("f-comm-9")}
    assert {"d-price-49", "d-halden-disc", "d-margin-target", "a-orla-quote", "t-billing-config"} <= rad
    assert not rad & {"d-hire-2", "d-corvane", "a-pike-quote"}   # unrelated decisions must NOT be flagged

def test_correction_supersedes_never_deletes():
    seed()
    agent.run(emit=lambda e: None, do_rejudge=False)
    assert T.get_fact("f-comm-9")["status"] == "superseded"
    assert T.get_fact("f-comm-12")["status"] == "current"

def test_detail_returns_owner_and_doc():
    seed()
    d = T.detail("t-billing-config")
    assert d["kind"] == "Task" and d["owner"] == "Leo Novak" and d["doc_id"] == "doc-14"
    assert "error" in T.detail("nope-1")

def test_multihop_tasks_and_owners_downstream():
    # The multi-hop demo question, extractively: tasks+decisions downstream of f-comm-9, with owners.
    seed()
    chains = {n["id"]: T.detail(n["id"]) for n in T.blast_radius("f-comm-9") if n["kind"] in ("Task", "Decision")}
    assert chains["t-billing-config"]["owner"] == "Leo Novak"
    assert chains["d-price-49"]["owner"] == "Elena Ruiz"
    assert "t-hire-reqs" not in chains  # unaffected subtree stays out
