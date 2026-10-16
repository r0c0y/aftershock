import os
from falkordb import FalkorDB

GRAPH = os.environ.get("AFTERSHOCK_GRAPH", "aftershock")

def graph():
    host = os.environ.get("FALKORDB_HOST", "localhost")
    port = int(os.environ.get("FALKORDB_PORT", "6379"))
    return FalkorDB(host=host, port=port).select_graph(GRAPH)

def rows(res):
    """Convert a FalkorDB result set to a list of dicts keyed by header names."""
    names = [h[1] if isinstance(h, (list, tuple)) else h for h in res.header]
    return [dict(zip(names, r)) for r in res.result_set]
