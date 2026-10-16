"""Graph-OFF baseline: flat keyword retrieval (BM25) over document text only. No edges, no states."""
import math, re
from collections import Counter
from .seed import load_documents

STOP = set("the a an of to in and or is are for on at by with from be as it this that was".split())

def tok(s):
    return [w for w in re.findall(r"[a-z0-9%$.]+", s.lower()) if w not in STOP]

class Flat:
    def __init__(self):
        self.docs = load_documents()
        self.toks = [tok(d["title"] + " " + d["body"]) for d in self.docs]
        self.N = len(self.docs)
        self.avg = sum(map(len, self.toks)) / self.N
        df = Counter(w for t in self.toks for w in set(t))
        self.idf = {w: math.log(1 + (self.N - n + .5) / (n + .5)) for w, n in df.items()}

    def search(self, query, k=3, k1=1.5, b=.75):
        q = tok(query)
        out = []
        for d, t in zip(self.docs, self.toks):
            tf = Counter(t)
            s = sum(self.idf.get(w, 0) * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / self.avg)) for w in q if w in tf)
            out.append((s, d))
        out.sort(key=lambda x: -x[0])
        return [{"score": round(s, 2), "id": d["id"], "title": d["title"], "state": d["state"], "body": d["body"]} for s, d in out[:k]]
