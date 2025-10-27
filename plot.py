# do not call these function, not inteded to be used generally.

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from collections import Counter

import math
import re
import numpy as np

def _most_pop_experiences():
    import dataset
    dataset.load()

    popular_experiences = sorted(
        list(dataset.games.values()), key=lambda g: g["favorite"], reverse=True
    )

    top_n = 30
    top = popular_experiences[:top_n]

    def clean_title(game):
        title = game["title"]
        _title = re.sub(r"\(.*?\)", "", title)
        _title = re.sub(r"\[.*?\]", "", _title)
        _title = _title.strip()
        if not _title:
            _title = title

        genres = game.get("genres", [])
        if len(genres) > 1:
            genre_field = genres[1]
            if "Simulation" in genre_field:
                _title = "♣" + _title
            elif "Obby" in genre_field:
                _title = "♠" + _title
            elif "Adventure" in genre_field:
                _title = "♦" + _title

        return _title

    titles = [clean_title(g) for g in top]
    favorites = [g["favorite"] for g in top]

    palette = [
        "#8d2448", "#b64c69", "#ce949b", "#ba9aa0", "#ce7d5f",
        "#f2be82", "#f9dbb9", "#fcf1e3"
    ]

    colors = palette[:len(favorites)]
    if len(favorites) > len(palette):
        cmap = LinearSegmentedColormap.from_list("custom", palette)
        colors = [cmap(i / (len(favorites) - 1)) for i in range(len(favorites))]

    _, ax = plt.subplots(figsize=(5, 5))
    ax.barh(
        titles[::-1],
        favorites[::-1],
        color=colors[::-1],
        edgecolor='black',
        linewidth=1
    )

    ax.set_xlabel("Number of Favorites", fontsize=10)
    ax.set_ylabel("Experience Title", fontsize=10)
    ax.tick_params(axis='y', labelsize=7)
    ax.tick_params(axis='x', labelrotation=30, labelsize=8)

    max_fav = max(favorites)
    step = max(max_fav // 9, 1)
    ax.set_xticks(range(0, max_fav + step, step))
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("data/plot/bar-pop.png", dpi=300, bbox_inches="tight")
    plt.close()

def _distrib_kumaraswamy():
    def kumaraswamy(x, alpha, beta):
        x = np.clip(x, 1e-6, 1-1e-6)
        y = alpha * beta * (x ** (alpha - 1)) * ((1 - x ** alpha) ** (beta - 1))
        y /= np.max(y)
        return 1 + y

    x = np.linspace(0, 1, 500)

    y1 = kumaraswamy(x, 0.85, 0.85)
    y2 = kumaraswamy(x, 1.5, 5)

    plt.figure(figsize=(6,4))

    plt.plot(x, y1, lw=1.5, color="#8d2448", label=f"α=0.85, β=0.85")
    plt.plot(x, y2, lw=1.5, color="#db2556", label=f"α=1.5, β=5")
    
    plt.fill_between(x, 1, y1, color="#8d2448", alpha=0.2)
    plt.fill_between(x, 1, y2, color="#db2556", alpha=0.2)

    plt.xlabel("Normalized Popularity")
    plt.ylabel("Multiplier")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.legend()
    plt.tight_layout()
    plt.savefig("data/plot/kumaraswamy.png", dpi=300, bbox_inches="tight")

def _distrib_beta():
    def beta_weight(popularity, alpha=2, beta=2):
        popularity = np.clip(popularity, 1e-6, 1 - 1e-6)
        weights = (popularity ** (alpha - 1)) * ((1 - popularity) ** (beta - 1))
        weights /= weights.max()
        return 1 + weights
    
    x = np.linspace(0, 1, 501)

    plt.figure(figsize=(6, 4))
    plt.plot(x, beta_weight(x, 2, 5), lw=1.5, color="#8d2448", label="α=?, β=?")
    plt.plot(x, beta_weight(x, 5, 2), lw=1.5, color="#8d2448", label="α=?, β=?")
    plt.plot(x, beta_weight(x, .75, .75), lw=1.5, color="#db2556", label="α=?, β=?")
    plt.plot(x, beta_weight(x, .85, .85), lw=1.5, color="#db2556", label="α=?, β=?")

    plt.xlabel("Normalized Popularity")
    plt.ylabel("Beta Multiplier")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig("data/plot/beta.png", dpi=300, bbox_inches="tight")

def _distrib_gaussian():
    def gaussian(x, center, width):
        return 1 + math.exp(-0.5 * ((x - center) / width) ** 2)

    x = [i / 500 for i in range(501)]

    y_a = [gaussian(v, center=.825, width=.3) for v in x]
    y_b = [gaussian(v, center=.665, width=.4) for v in x]

    plt.figure(figsize=(6, 4))
    plt.plot(x, y_a, lw=1.5, color="#8d2448")
    plt.plot(x, y_b, lw=1.5, color="#db2556")

    plt.axvline(.825, color="#8d2448", linestyle="--", lw=1.25)
    plt.axvline(.665, color="#db2556", linestyle="--", lw=1.25)

    plt.xlabel("Normalized Popularity")
    plt.ylabel("Gaussian Multiplier")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.legend()
    plt.tight_layout()
    plt.savefig("data/plot/gaussian.png", dpi=300, bbox_inches="tight")

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

    for (xv, game_x), (yv, game_y) in zip(freq["x"], freq["y"]):
        id = game_x["id"]
        plt.text(
            xv,
            yv - 0.0005,
            id,
            fontsize=5,
            ha="center",
            va="top",
            alpha=0.6,
        )
    plt.savefig("data/plot/scatter-debug.png", dpi=300, bbox_inches="tight")

    most = []
    for x, y in zip(freq["x"], freq["y"]):
        expe = x[1]
        diff = abs(x[0] - y[0])

        most.append((diff, expe))

    from pprint import pprint

    most.sort(key=lambda f: f[0], reverse=True)
    pprint([(f[0], f[1]["id"], f[1]["title"]) for f in most[:20]])
