import recsys.dataset
import recsys.nlp

import torch
import sentence_transformers.util
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-mpnet-base-v2
__model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    for game in recsys.dataset.__games.values():
        if "__embed" in game:
            continue
        
        game["__embed"] = __model.encode(recsys.nlp.lemmatize(game), convert_to_tensor=True)

def similar(game_id: int, k: int = 10) -> list[str]:
    __pre_compute_embeddings()

    similarities: list[tuple] = []
    for game in recsys.dataset.__games.values():
        if game["id"] == game_id:
            continue

        similarity = sentence_transformers.util.cos_sim(recsys.dataset.game_get(game_id)["__embed"], game["__embed"]).item()
        similarities.append((similarity, game["title"]))
    
    # TODO: we should use sorted list
    return sorted(similarities, key=lambda x: x[0], reverse=True)[:k]
