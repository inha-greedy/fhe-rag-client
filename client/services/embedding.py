from transformers import BertTokenizer, BertModel
import numpy as np


def embed_sentence(sentence: str) -> np.ndarray:
    """
    sentence를 받아와 임베딩합니다.
    """

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")

    encoded = tokenizer.encode_plus(sentence, return_tensors="pt")
    output = model(**encoded)

    embedding = output.last_hidden_state[:, 0, :].detach().numpy().flatten()
    n_embedding = _normalize_vector(embedding)

    return n_embedding


def _normalize_vector(v1: np.ndarray) -> np.ndarray:
    v1_norm = np.linalg.norm(v1)
    v1_normalized = v1 / v1_norm

    return v1_normalized
