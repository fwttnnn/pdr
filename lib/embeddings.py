import os
import concurrent.futures

import pickle
import torch

EMBEDDINGS_FILEPATH = "data/embeddings.pkl"

def load(path: str = EMBEDDINGS_FILEPATH) -> dict:
    if not os.path.exists(path):
        with open(path, "wb") as f:
            pickle.dump({}, f)

    with open(path, "rb") as f:
        embeddings = pickle.load(f)
        return embeddings
    
def save(embeddings, path: str = EMBEDDINGS_FILEPATH):
    with open(path, "wb") as f:
        pickle.dump(embeddings, f)

def precompute(path: str = EMBEDDINGS_FILEPATH):
    import nlp, dataset
    from model import model

    if not dataset.embeddings:
        dataset.embeddings = load()

    def __compute_emb(id: int):
        print(f"Risperidone: generating embeddings for {id}")
        dataset.embeddings[id] = model.encode(nlp.lemmatize(dataset.games[id]), convert_to_tensor=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        executor.map(__compute_emb, [id for id in dataset.games.keys() if id not in dataset.embeddings])
    
    save(dataset.embeddings, path)

# kinda stolen from sentence_transformer.util, credit on that
def similarity(a: torch.Tensor, b: torch.Tensor):
    """
    Compute embedding's cosine similarity.
    """

    def unsqueeze(emb: torch.Tensor):
        if emb.dim() == 1:
            emb = emb.unsqueeze(0)

        return emb

    def normalize(emb: torch.Tensor):
        return torch.nn.functional.normalize(emb, p=2, dim=1)

    return torch.mm(normalize(unsqueeze(a)), normalize(unsqueeze(b)).transpose(1, 0))
