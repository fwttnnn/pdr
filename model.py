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

    def _metric_outliers(similarities):
        similarities = np.array(similarities)
        med = np.median(similarities)
        mad = np.median(np.abs(similarities - med)) + 1e-8
        mod_z = 0.6745 * (similarities - med) / mad
        outlier_mask = mod_z < -3.5
        outlier_rate = np.mean(outlier_mask)
        return float(outlier_rate)

    # without squeezing, wanted to do tests
    if False:
        top_k = sorted(zip(similarities, games), key=lambda x: x[0], reverse=True)[:k]
        top_k_ids =[ gid for _, gid in top_k]
        return top_k_ids, _metric_outliers([sim for sim, _, in top_k])

    def _normalize_popularities(raw_popularities):
        mean_p = np.mean(raw_popularities)
        std_p  = np.std(raw_popularities) + 1e-8

        pops = [1 / (1 + math.exp(-(p - mean_p) / (2 * std_p))) for p in raw_popularities]

        min_p, max_p = min(pops), max(pops)
        pops = [(p - min_p) / (max_p - min_p + 1e-8) for p in pops]

        return pops
    
    def _boost_popularities(popularities, center=0.70, width=0.25, scale=1.5):
        """ bell curve boosting
        """
        assert(center >= 0 and center <= 1)

        adjusted = []

        for p in popularities:
            factor = math.exp(- ((p - center) ** 2) / (2 * width ** 2))
            _p = p * (1 + (factor - 0.5) * scale)
            _p = max(0.0, min(1.0, _p))
            adjusted.append(_p)

        return adjusted

    popularities = [g["favorite"] for g in candidates]
    popularities = _normalize_popularities(popularities)
    popularities = _boost_popularities(popularities)

    COSINE_SIMILARITY_WEIGHT = 1.00
    GAME_POPULARITY_WEIGHT   = 0.10
    CANDIDATE_PRE_RANK_LIMIT = 500

    predictions = sorted(
        zip(similarities, popularities, games),
        key=lambda x: x[0],
        reverse=True
    )[:CANDIDATE_PRE_RANK_LIMIT]

    predictions = [
        (COSINE_SIMILARITY_WEIGHT * sim + GAME_POPULARITY_WEIGHT * pop, sim, gid)
        for sim, pop, gid in predictions
    ]
    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)

    top_k = predictions[:k]
    top_k_ids = [gid for _, _, gid in top_k]

    return top_k_ids, _metric_outliers([sim for _, sim, _ in top_k])

def similar(game_ids: list[int], k: int = 10) -> list[int]:
    recommendations, _ = __debug_similar(game_ids, k)
    return recommendations
