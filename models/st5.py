from sentence_transformers import SentenceTransformer
import torch

st5 = None

def load():
    global st5
    st5 = SentenceTransformer("sentence-transformers/sentence-t5-base")
    return st5

def __encode(t: str | list[str]) -> torch.Tensor:
    return st5.encode(t, convert_to_tensor=True)
