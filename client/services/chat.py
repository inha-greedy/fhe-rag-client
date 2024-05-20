import os
from typing import List, Tuple
import time
import numpy as np
import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv
from Pyfhel import PyCtxt, Pyfhel

from ..models.document import PyCDocumentDto
from ..models.similarity import PyCSimilarity, PyCSimilarityDto, Similarity
from .document import embed_documents, encrypt_documents, send_documents, split_content
from .key import load_he_from_key
from .session import set_content, get_user_id


def get_similarities_from_server(query: str) -> List[PyCSimilarity]:
    he = load_he_from_key()

    encrypted_query_document = _make_query_document(query=query)

    response = send_documents(
        uri="/get-similarities",
        encrypted_documents=[encrypted_query_document],
    ).json()

    received_similarities = [PyCSimilarityDto(**item).to_similarity(he=he) for item in response]
    return received_similarities


def decrypt_similarities(
    encrypted_similarities: List[PyCSimilarity],
) -> Tuple[List[Similarity], float]:
    he = load_he_from_key()

    similarities = []
    decrypt_times = []

    for sim in encrypted_similarities:
        start_time = time.time()
        score = he.decrypt(sim.score)[0]
        end_time = time.time()
        decrypt_time = end_time - start_time
        decrypt_times.append(decrypt_time)

        if score > 1 + 1 or score < 0 - 1:
            print("warning - step 2: key sync not matched.")
            set_content("no_sync", True)
            return ([], 0.0)

        similarities.append(Similarity(index=sim.index, score=score))

    avg_decrypt_time = sum(decrypt_times) / len(decrypt_times) if decrypt_times else 0.0

    return similarities, round(avg_decrypt_time, 3)


def choose_indices(similarities: List[Similarity], top_k: int) -> List[int]:
    sorted_similarities = sorted(similarities, key=lambda x: x.score, reverse=True)
    print(f"{sorted_similarities=}")

    indices: List[int] = [sim.index for sim in sorted_similarities[:top_k]]

    return indices


def send_indices_and_receive_contexts(indices: List[int]) -> List[str]:
    he = load_he_from_key()

    load_dotenv()

    server_url = os.getenv("SERVER_URL") or "EMPTY"
    user_id = get_user_id()
    headers = {"origin": user_id}

    response = requests.post(
        server_url + "/get-docs", headers=headers, json=indices, timeout=120
    ).json()

    received_documents = [PyCDocumentDto(**item).to_document(he=he) for item in response]

    contexts = []

    for doc in received_documents:
        document = doc.document
        decrypted_document = decrypt_result(he, document)
        pure_document = _numpy_to_string(decrypted_document)
        contexts.append(pure_document)

    return contexts


def _make_query_document(query: str):
    splitted_documents = split_content(str_content=query)

    documents, _ = embed_documents(documents=splitted_documents)

    encrypted_documents, _ = encrypt_documents(documents=documents)

    return encrypted_documents[0]


def decrypt_result(he: Pyfhel, c_result: PyCtxt) -> np.ndarray:
    return he.decrypt(c_result)


def _numpy_to_string(numpy_to_convert: np.ndarray) -> str:
    decrypted_chars = []
    for num in numpy_to_convert:
        try:
            rounded_num = int(round(num))
            char = chr(rounded_num)
        except OverflowError:
            print("warning - step 3: key sync not matched.")
            set_content("no_sync", True)
            return "<NO_CONTEXT>"

        if char != "\x00":  # Skip null characters
            decrypted_chars.append(char)
    decrypted_str = "".join(decrypted_chars)

    return decrypted_str
