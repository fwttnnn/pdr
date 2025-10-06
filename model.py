import dataset
import embeddings

import torch

import numpy as np
import math

def __debug_similar(game_ids: list[int], k: int = 10) -> tuple[list[int], float]:
    __set_game_ids = set(game_ids)

    user_embedding = torch.mean(
        torch.stack([dataset.embeddings[g] for g in game_ids]), dim=0
    )

    __games_all_sorted = sorted(dataset.games.values(), key=lambda g: g["id"])
    candidates = [g for g in __games_all_sorted if g["id"] not in __set_game_ids]
    games = [g["id"] for g in candidates]

    __embeddings = torch.stack([dataset.embeddings[g] for g in games])
    similarities = embeddings.similarity(user_embedding, __embeddings).squeeze(0).tolist()

    # without squeezing, wanted to do tests
    if False:
        top_k = sorted(zip(similarities, games), key=lambda x: x[0], reverse=True)[:k]
        divergence = float(torch.mean(torch.tensor([1 - sim for sim, _ in top_k])))
        return [gid for _, gid in top_k], divergence

    def _squeeze_popularities(raw_popularities, squeeze=0.90):
        mean_p = np.mean(raw_popularities)
        std_p  = np.std(raw_popularities) + 1e-8

        pops = [1 / (1 + math.exp(-(p - mean_p) / (2 * std_p))) for p in raw_popularities]

        min_p, max_p = min(pops), max(pops)
        pops = [(p - min_p) / (max_p - min_p + 1e-8) for p in pops]

        pops = [0.5 + (p - 0.5) * squeeze for p in pops]
        return pops

    popularities = [g["favorite"] for g in candidates]
    popularities = _squeeze_popularities(popularities)

    COSINE_SIMILARITY_WEIGHT = 1.00
    GAME_POPULARITY_WEIGHT   = 0.10
    CANDIDATE_PRE_RANK_LIMIT = 500

    predictions = sorted(
        zip(similarities, popularities, games),
        key=lambda x: x[0],
        reverse=True
    )[:k + CANDIDATE_PRE_RANK_LIMIT]

    predictions = [
        (COSINE_SIMILARITY_WEIGHT * sim + GAME_POPULARITY_WEIGHT * pop, sim, gid)
        for sim, pop, gid in predictions
    ]
    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)

    top_k = predictions[:k]

    divergence = float(torch.mean(torch.tensor([1 - sim for _, sim, _ in top_k])))
    top_k_ids = [gid for _, _, gid in top_k]

    return top_k_ids, divergence

def similar(game_ids: list[int], k: int = 10) -> list[int]:
    recommendations, _ = __debug_similar(game_ids, k)
    return recommendations
