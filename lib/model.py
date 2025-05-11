import dataset
import nlp

import torch
import sentence_transformers.util
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-mpnet-base-v2
model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    for id, embedding in dataset.__load_embeddings().items():
        dataset.games[id]["__embed"] = embedding

    added = False
    for game in dataset.games.values():
        if "__embed" in game:
            continue
        
        added = True
        game["__embed"] = model.encode(nlp.lemmatize(game), convert_to_tensor=True)

    if added:
        dataset.__save_embeddings()

dataset.__load()
__pre_compute_embeddings()

def similar(game_ids: list[int], k: int = 10) -> list[tuple]:
    predictions: list[tuple] = []

    game_ids = set(game_ids)
    embeddings = [game["__embed"] for game in dataset.games.values() if game["id"] in game_ids]

    min_popularity = dataset.games[game_ids[0]]["favorite"]
    max_popularity = dataset.games[game_ids[0]]["favorite"]

    for game in dataset.games.values():
        popularity = game["favorite"]
        min_popularity = min(min_popularity, popularity)
        max_popularity = max(max_popularity, popularity)

        if game["id"] in game_ids:
            continue

        similarities = [sentence_transformers.util.cos_sim(embedding, game["__embed"]).item() for embedding in embeddings]
        predictions.append((torch.mean(torch.tensor(similarities)), game["id"]))
    
    COSINE_SIMILARITY_WEIGHT = 0.7
    GAME_POPULARITY_WEIGHT = (1 - COSINE_SIMILARITY_WEIGHT)

    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)[:k+50]
    predictions = sorted(predictions, key=lambda p: COSINE_SIMILARITY_WEIGHT * float(p[0]) + GAME_POPULARITY_WEIGHT * ((dataset.games[p[1]]["favorite"] - min_popularity) / (max_popularity - min_popularity)), reverse=True)
    return [pred[1] for pred in predictions][:k]
