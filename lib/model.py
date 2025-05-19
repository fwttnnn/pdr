import dataset
import embeddings
import nlp

import threading
import torch
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-mpnet-base-v2
model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    dataset.embeddings = embeddings.load()

    def batch(lst: list, n: int) -> list[list]:
        return [lst[i:i + n] for i in range(0, len(lst), n)]
    
    def generate_embedding(game_id: int):
        print(f"Risperidone: generating embeddings for {game_id}")
        dataset.embeddings[game_id] = model.encode(nlp.lemmatize(dataset.games[game_id]), convert_to_tensor=True)

    for chunk in batch([id for id in dataset.games.keys() if id not in dataset.embeddings], 10):
        threads = [threading.Thread(target=generate_embedding, args=(id, )) for id in chunk]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    embeddings.save(dataset.embeddings)

dataset.__load()
__pre_compute_embeddings()

def similar(game_ids: list[int], k: int = 10) -> list[tuple]:
    predictions: list[tuple] = []

    min_popularity = dataset.games[game_ids[0]]["favorite"]
    max_popularity = dataset.games[game_ids[0]]["favorite"]

    __set_game_ids = set(game_ids)
    user_embedding = torch.mean(torch.stack([dataset.embeddings[id] for id in game_ids]), dim=0)

    for game in dataset.games.values():
        popularity = game["favorite"]
        min_popularity = min(min_popularity, popularity)
        max_popularity = max(max_popularity, popularity)

        if game["id"] in __set_game_ids:
            continue

        predictions.append((embeddings.similarity(user_embedding, dataset.embeddings[game["id"]]), game["id"]))
    
    COSINE_SIMILARITY_WEIGHT = 0.7
    GAME_POPULARITY_WEIGHT = (1 - COSINE_SIMILARITY_WEIGHT)

    predictions = sorted(predictions, key=lambda x: x[0], reverse=True)[:k+50]
    predictions = sorted(predictions, key=lambda p: COSINE_SIMILARITY_WEIGHT * float(p[0]) + GAME_POPULARITY_WEIGHT * ((dataset.games[p[1]]["favorite"] - min_popularity) / (max_popularity - min_popularity)), reverse=True)
    return [pred[1] for pred in predictions][:k]
