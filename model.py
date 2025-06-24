import dataset
import embeddings

import torch
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-mpnet-base-v2 | all-distilroberta-v1 | distiluse-base-multilingual-cased-v2
model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def similar(game_ids: list[int], k: int = 10) -> list[int]:
    predictions: list[tuple] = []

    __set_game_ids = set(game_ids)
    user_embedding = torch.mean(torch.stack([dataset.embeddings[id] for id in game_ids]), dim=0)

    __games_all_sorted = sorted(dataset.games.values(), key=lambda g: g["id"])
    games = [g["id"] for g in __games_all_sorted if g["id"] not in __set_game_ids]
    popularities = [g["favorite"] for g in __games_all_sorted if g["id"] not in __set_game_ids]

    min_popularity = min(popularities)
    max_popularity = max(popularities)
    popularities = [(p - min_popularity) / ((max_popularity - min_popularity) + 1e-8) for p in popularities]

    __embeddings = torch.stack([dataset.embeddings[game_id] for game_id in games])
    similarities = embeddings.similarity(user_embedding, __embeddings).squeeze(0)

    COSINE_SIMILARITY_WEIGHT = 0.90
    GAME_POPULARITY_WEIGHT = 0.25

    CANDIDATE_PRE_RANK_LIMIT = 5000

    predictions = list(zip(similarities.tolist(), popularities, games))
    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)
    predictions = predictions[:k + CANDIDATE_PRE_RANK_LIMIT]

    predictions = [(COSINE_SIMILARITY_WEIGHT * sim + GAME_POPULARITY_WEIGHT * pop, gid) for sim, pop, gid in predictions]
    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)
    return [gid for _, gid in predictions[:k]]
