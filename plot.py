# do not call these function, not inteded to be used generally.

import matplotlib.pyplot as plt
from collections import Counter

def bar():
    import dataset
    dataset.load()

    import matplotlib.pyplot as plt
    import numpy as np

    genres = {}
    for g in dataset.games.values():
        genre: str = g["genres"][1].split(" &")[0]

        if not genre:
            continue

        genres[genre] = genres.get(genre, 0) + 1

    _sorted = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    _genres = [g for g, _ in _sorted]
    _counts = [c for _, c in _sorted]

    palette = ["#8d2448", "#b64c69", "#ce949b", "#ba9aa0", "#ce7d5f",
            "#f2be82", "#f9dbb9", "#fcf1e3"]

    colors = palette[:len(_counts)]
    if len(_counts) > len(palette):
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list("custom", palette)
        colors = [cmap(i / (len(_counts) - 1)) for i in range(len(_counts))]

    _, ax = plt.subplots(figsize=(4, 3))
    ax.bar(
        _genres,
        _counts,
        color=colors,
        edgecolor='black',
        linewidth=1
    )

    # ax.set_ylabel("Number of Experiences")
    # plt.xticks(rotation=90, ha='right')

    ax.set_ylabel("Number of Experiences", fontsize=10)
    ax.tick_params(axis='x', labelrotation=90, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)

    manual_step = 2000
    max_count = max(_counts)
    max_grid = (max_count // manual_step + 1) * manual_step
    ax.set_yticks(np.arange(0, max_grid + 1, manual_step))
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("data/plot/bar.png", dpi=300, bbox_inches="tight")
    plt.savefig("paper/ieee/bar-genres.png", dpi=300, bbox_inches="tight")

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
