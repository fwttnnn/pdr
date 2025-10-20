import dataset
import embeddings

import torch

import numpy as np
import math

def similar(game_ids: list[int]) -> list[tuple[int, int]]:
    __set_game_ids = set(game_ids)

    user_embedding = torch.mean(torch.stack([dataset.embeddings[g] for g in game_ids]), dim=0)

    __games_all_sorted = sorted(dataset.games.values(), key=lambda g: g["id"])
    candidates = [g for g in __games_all_sorted if g["id"] not in __set_game_ids]
    games: list[int] = [g["id"] for g in candidates]

    __embeddings = torch.stack([dataset.embeddings[g] for g in games])
    similarities = embeddings.similarity(user_embedding, __embeddings).squeeze(0).tolist()
    similarities = sorted(zip(similarities, games), key=lambda x: x[0], reverse=True)

    return similarities

def rank(similarities: list[tuple[int, int]]):
    sims: list[int]         = [sim for sim, _ in similarities]
    games: list[object]     = [gid for _, gid in similarities]
    popularities: list[int] = [dataset.games[gid]["favorite"] for gid in games]

    def _normalize_popularities(_popularities):
        mean_p = np.mean(_popularities)
        std_p  = np.std(_popularities) + 1e-8

        pops = [1 / (1 + math.exp(-(p - mean_p) / (2 * std_p))) for p in _popularities]

        min_p, max_p = min(pops), max(pops)
        pops = [(p - min_p) / (max_p - min_p + 1e-8) for p in pops]

        return pops
    
    def _boost_popularities(_popularities, center=0.665, width=0.4):
        """ bell curve boosting
        """
        assert(center >= 0 and center <= 1)

        adjusted = []

        for p in _popularities:
            p = 1 + math.exp(-0.5 * ((p - center) / width) ** 2)
            adjusted.append(p)

        return adjusted

    popularities = _normalize_popularities(popularities)
    popularities = _boost_popularities(popularities)

    COSINE_SIMILARITY_WEIGHT = 1.00
    GAME_POPULARITY_WEIGHT   = 0.10
    CANDIDATE_PRE_RANK_LIMIT = 500

    ranked = sorted(zip(sims, popularities, games),
                        key=lambda x: x[0],
                        reverse=True)[:CANDIDATE_PRE_RANK_LIMIT]

    ranked = [(COSINE_SIMILARITY_WEIGHT * sim + GAME_POPULARITY_WEIGHT * pop, gid)
              for sim, pop, gid in ranked]

    ranked = sorted(ranked, key=lambda x: x[0], reverse=True)
    ranked = [gid for _, gid in ranked]

    return ranked

def recommend(game_ids: list[int], k: int = 10) -> list[int]:
    similarities = similar(game_ids)
    ranked       = rank(similarities)

    return ranked[:k]
