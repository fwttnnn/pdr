import matplotlib.pyplot as plt
from collections import Counter

def histogram(experiences):
    flatten = []
    for values in experiences:
        [flatten.append(v) for v in values]
    
    return

def scatter(recommendations: list[list[int]], truths: list[list[int]]):
    def _occurance(lst: list[list[int]]) -> dict[int, float]:
        flatten = []
        for values in lst:
            [flatten.append(v) for v in values]
        
        total = len(flatten)
        occurance = dict(Counter(flatten))

        return {k: v / total for k, v in occurance.items()}
    
    recommendations = _occurance(recommendations)
    truths          = _occurance(truths)

    ids  = set(list(recommendations.keys()) + list(truths.keys()))
    freq = {
        "x": [],
        "y": [],
    }

    import dataset
    for id in ids:
        freq["x"].append((truths[id], dataset.games[id])
                         if id in truths
                         else (0, dataset.games[id]))
        freq["y"].append((recommendations[id], dataset.games[id])
                         if id in recommendations
                         else (0, dataset.games[id]))

    x = [f[0] for f in freq["x"]]
    y = [f[0] for f in freq["y"]]

    plt.figure(figsize=(4, 5))

    plt.scatter(
        x,
        y,
        color="#8d2448",
        edgecolors="#000",
        linewidths=0.7,
        alpha=0.5,
    )

    plt.xlabel("User-Interest (%)")
    plt.ylabel("Recommendation (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig("data/plot/scatter.png", dpi=300, bbox_inches="tight")

    import config
    if not config.DEBUG:
        return

    most = []
    for x, y in zip(freq["x"], freq["y"]):
        expe = x[1]
        diff = abs(x[0] - y[0])

        most.append((diff, expe))

    from pprint import pprint

    most.sort(key=lambda f: f[0], reverse=True)
    pprint([(f[0], f[1]["id"], f[1]["title"]) for f in most[:20]])
