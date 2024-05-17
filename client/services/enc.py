from Pyfhel import Pyfhel, PyCtxt

import numpy as np

from .storage import get_content, set_content


def get_he_context() -> Pyfhel:

    return get_content("HE")


def set_he_context(he: Pyfhel = None) -> Pyfhel:

    if he is None:
        he = setup_ckks_context()

    return set_content("HE", he)


def setup_ckks_context(scale: int = 2**40) -> Pyfhel:

    he = Pyfhel()
    ckks_params = {
        "scheme": "CKKS",
        "n": 2**14,
        "scale": scale,
        "qi_sizes": [60, 30, 30, 30, 60],
    }
    he.contextGen(**ckks_params)
    he.keyGen()
    he.relinKeyGen()
    he.rotateKeyGen()

    return he


def encrypt_document(document: str) -> PyCtxt:

    emb = _string_to_numpy(document)

    return encrypt_embedding(emb)


def encrypt_embedding(embedding: np.ndarray) -> PyCtxt:
    he = get_he_context()

    n_slots = he.get_nSlots()
    ctxt = [
        he.encrypt(embedding[j : j + n_slots])
        for j in range(0, len(embedding), n_slots)
    ]

    return ctxt[0]


def _string_to_numpy(str_to_convert: str) -> np.ndarray:
    arr_str = np.array([ord(c) for c in str_to_convert], dtype=np.float64)
    return arr_str


def _numpy_to_string(numpy_to_convert: np.ndarray) -> str:
    decrypted_str = "".join([chr(int(round(c))) for c in numpy_to_convert])
    return decrypted_str
