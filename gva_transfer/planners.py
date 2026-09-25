"""Search code receives scores and branch handles only, never live physical parameters."""
def rank(score,aid): return score,aid==0,-aid

def greedy(query,remaining):
    batch=query(None)
    winner=max(batch.ids,key=lambda aid:rank(batch.scores[aid],aid))
    return winner,batch.scores[winner]

def beam2(query,remaining):
    first=query(None)
    ordered=sorted(first.ids,key=lambda aid:rank(first.scores[aid],aid),reverse=True)
    if remaining==1: return ordered[0],first.scores[ordered[0]]
    best=None
    for aid in ordered[:2]:
        second=query(first.handles[aid])
        for bid,score in zip(second.ids,second.scores):
            total=tuple(first.scores[aid][j]+score[j] for j in range(2))
            key=(total,aid==0,-aid,bid==0,-bid)
            if best is None or key>best[0]: best=(key,aid,total)
    return best[1],best[2]
