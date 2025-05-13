import os
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
