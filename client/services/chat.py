from typing import List

from Pyfhel import Pyfhel, PyCtxt

from ..services.document import (
    split_content,
    embed_documents,
    encrypt_documents,
    send_documents_to_server,
)
from ..services.storage import get_content
from ..services.enc import get_he_context

from ..models.document import PyCDocumentDto
from ..models.similarity import Similarity, PyCSimilarity


def send_query_and_receive_encrypted_similarity(query: str) -> List[PyCSimilarity]:

    encrypted_query_document = make_query_document(query=query)

    if False:

        response = send_documents_to_server(
            uri="/emb-query",
            encrypted_documents=[encrypted_query_document],
        )

        received_c_top_k = response.json()  # List[PyCSimilarityDto]
    elif False:

        c_query_document = encrypted_query_document.to_document()
        stored_encrypted_documents = get_content("s4")

        he = get_he_context()

        received_c_top_k = []

        for doc in stored_encrypted_documents:

            c_score = _compute_cosine_similarity(
                c_query_document.embedding, doc.to_document().embedding
            )

            similarity = PyCSimilarity(index=doc.index, score=c_score)
            received_c_top_k.append(similarity)

    else:
        received_c_top_k = []

    # received_c_top_k

    return received_c_top_k


def make_query_document(query: str):
    splitted_documents = split_content(str_content=query)

    documents = embed_documents(documents=splitted_documents)

    encrypted_documents = encrypt_documents(documents=documents)

    return encrypted_documents[0]


def receive_encrypted_top_k(encrypted_query_document: PyCDocumentDto):

    if False:

        response = send_documents_to_server(
            uri="/emb-query",
            encrypted_documents=[encrypted_query_document],
        )

        received_c_similarity = response.json()  # List[PyCSimilarityDto]
    else:

        c_query_document = encrypted_query_document.to_document()

        stored_encrypted_documents = get_content("s4")  # List[PyCSimilarityDto]
        he = get_he_context()

        received_c_similarity = []

        for doc in stored_encrypted_documents:

            c_score = _compute_cosine_similarity(
                c_query_document.embedding, doc.to_document().embedding
            )

            similarity = PyCSimilarity(index=doc.index, score=c_score)

            received_c_similarity.append(similarity)

    # received_c_top_k

    return received_c_similarity


def decrypt_result(he: Pyfhel, c_result: PyCtxt) -> float:
    return he.decrypt(c_result)


def _compute_cosine_similarity(ctxt_v1: PyCtxt, ctxt_v2: PyCtxt) -> PyCtxt:
    c_result = ctxt_v1 @ ctxt_v2
    return c_result
