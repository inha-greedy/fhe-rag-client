import os
from typing import List

import numpy as np
import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv
from Pyfhel import PyCtxt, Pyfhel

from ..models.document import PyCDocumentDto
from ..models.similarity import PyCSimilarity, PyCSimilarityDto, Similarity
from ..services.document import embed_documents, encrypt_documents, send_documents, split_content
from ..services.enc import get_he_context


def get_similarities_from_server(query: str) -> List[PyCSimilarity]:
    encrypted_query_document = _make_query_document(query=query)

    response = send_documents(
        uri="/get-similarities",
        encrypted_documents=[encrypted_query_document],
    ).json()

    received_similarities = [PyCSimilarityDto(**item).to_similarity() for item in response]
    return received_similarities


def decrypt_similarities(
    encrypted_similarities: List[PyCSimilarity],
) -> List[Similarity]:
    he = get_he_context()

    similarities = []
    for sim in encrypted_similarities:
        score = he.decrypt(sim.score)
        similarities.append(Similarity(index=sim.index, score=score[0]))

    return similarities


def choose_indices(similarities: List[Similarity], num_context: int) -> List[int]:
    sorted_similarities = sorted(similarities, key=lambda x: x.score, reverse=True)
    print(f"{sorted_similarities=}")

    indices: List[int] = [sim.index for sim in sorted_similarities[:num_context]]

    return indices


def send_indices_and_receive_contexts(indices: List[int]) -> List[str]:
    load_dotenv()

    server_url = os.getenv("SERVER_URL") or "EMPTY"

    response = requests.post(server_url + "/get-docs", json=indices, timeout=9).json()

    received_documents = [PyCDocumentDto(**item).to_document() for item in response]

    he = get_he_context()
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


def decrypt_result(he: Pyfhel, c_result: PyCtxt) -> float:
    return he.decrypt(c_result)


def _numpy_to_string(numpy_to_convert: np.ndarray) -> str:
    decrypted_str = "".join(
        [chr(int(round(c))) for c in numpy_to_convert if chr(int(round(c))) != "\x00"]
    )
    return decrypted_str
