import gensim
import torch

# https://fasttext.cc/docs/en/crawl-vectors.html
ft_model_path = "cc.en.300.bin"
ft = gensim.models.fasttext.load_facebook_model(ft_model_path)

def __encode(text: str) -> torch.Tensor:
    words = text.lower().split()
    word_vecs = [torch.tensor(ft.wv[w], dtype=torch.float32) for w in words if w in ft.wv]

    if len(word_vecs) == 0:
        return torch.zeros(ft.vector_size, dtype=torch.float32)

    return torch.stack(word_vecs).mean(dim=0)
