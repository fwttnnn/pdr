import dataset
import embeddings

import torch
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-distilroberta-v1
model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def similar(game_ids: list[int], k: int = 10) -> list[tuple]:
    predictions: list[tuple] = []

    __set_game_ids = set(game_ids)
    user_embedding = torch.mean(torch.stack([dataset.embeddings[id] for id in game_ids]), dim=0)

    games = [g["id"] for g in dataset.games.values() if g["id"] not in __set_game_ids]
    popularities = [g["favorite"] for g in dataset.games.values() if g["id"] not in __set_game_ids]

    min_popularity = min(popularities)
    max_popularity = max(popularities)
    popularities = [(p - min_popularity) / ((max_popularity - min_popularity) + 1e-8) for p in popularities]

    __embeddings = torch.stack([dataset.embeddings[game_id] for game_id in games])
    similarities = embeddings.similarity(user_embedding, __embeddings).squeeze(0)

    COSINE_SIMILARITY_WEIGHT = 0.55
    GAME_POPULARITY_WEIGHT = (1 - COSINE_SIMILARITY_WEIGHT)

    predictions = list(zip(similarities.tolist(), popularities, games))
    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)[:k+50]
    predictions = sorted(predictions, key=lambda x: COSINE_SIMILARITY_WEIGHT * x[0] + GAME_POPULARITY_WEIGHT * x[1], reverse=True)[:k+50]
    return [pred[2] for pred in predictions][:k]
