"""EmbeddingGemma edge suggestion: for every Decision/Answer, rank Facts by cosine similarity.
Reports how many suggestions match the hand-authored (seeded) edges. Run: python -m aftershock.suggest_edges"""
import numpy as np
from . import seed_data as S
from .embed import embed

def run(k=2):
    facts = [(f[0], f[1]) for f in S.FACTS]
    F = embed([t for _, t in facts])
    items = [(d[0], d[1] + ". " + d[2], set(x for x in d[6])) for d in S.DECISIONS] + \
            [(a[0], a[1], set(x for x in a[3] if x.startswith("f-"))) for a in S.ANSWERS]
    # answers also depend on decisions; compare only the fact edges they carry directly
    hit = tot = sug = 0; rows_ = []
    for iid, text, truth in items:
        q = embed([text], "query")[0]
        sims = F @ q
        top = [facts[i][0] for i in np.argsort(-sims)[:k]]
        if truth:
            tot += len(truth); hit += len(truth & set(top))
        sug += len(top); rows_.append((iid, top, sorted(truth)))
    return rows_, hit, tot, sug

if __name__ == "__main__":
    r, hit, tot, sug = run()
    for x in r: print(x)
    print(f"seeded fact-edges recovered in top-2: {hit}/{tot}")
