import recsys.dataset
import recsys.nlp

import torch
import sentence_transformers.util
from sentence_transformers import SentenceTransformer

__model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    for game in recsys.dataset.__dataset.values():
        if "__embed" in game:
            continue
        
        game["__embed"] = __model.encode(recsys.nlp.lemmatize(game), convert_to_tensor=True)

def similar(game_id: int, k: int = 10) -> list[str]:
    __pre_compute_embeddings()
    __game_id = str(game_id)

    similarities: list[tuple] = []
    for game in recsys.dataset.__dataset.values():
        if game["id"] == __game_id:
            continue

        similarity = sentence_transformers.util.cos_sim(recsys.dataset.__dataset[game_id]["__embed"], game["__embed"]).item()
        similarities.append((similarity, game["title"]))
    
    # TODO: we should use sorted list
    return sorted(similarities, key=lambda x: x[0], reverse=True)[:k]

def predict(game_ids: list[int], k: int = 5) -> list[str]:
    __pre_compute_embeddings()

    game_ids = set(map(str, game_ids))
    embeddings = [game["__embed"] for game in recsys.dataset.__dataset.values() if game["id"] in game_ids]

    predictions: list[tuple] = []
    for game in recsys.dataset.__dataset.values():
        if game["id"] in game_ids:
            continue

        similarities = [sentence_transformers.util.cos_sim(embedding, game["__embed"]).item() for embedding in embeddings]
        predictions.append((torch.mean(torch.tensor(similarities)), game["title"]))

    # TODO: we should use sorted list
    return sorted(predictions, key=lambda x: x[0], reverse=True)[:k]
