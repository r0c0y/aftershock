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
