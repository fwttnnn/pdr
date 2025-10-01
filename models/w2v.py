from gensim.models import KeyedVectors
import torch

w2v_model_path = "GoogleNews-vectors-negative300.bin.gz"
w2v = KeyedVectors.load_word2vec_format(w2v_model_path, binary=True)

def __encode(text: str) -> torch.Tensor:
    words = [w for w in text.lower().split() if w in w2v]

    if not words:
        return torch.zeros(w2v.vector_size)

    vectors = torch.tensor([w2v[w] for w in words])
    return vectors.mean(dim=0)  # (300,)
