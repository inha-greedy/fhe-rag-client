import base64
import logging
import os
import time
from typing import List, Tuple
import io
import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv
from fastapi import UploadFile
from PyPDF2 import PdfReader
import docx
import numpy as np
from Pyfhel import PyCtxt

from .storage import load_he_from_key

from ..models.document import Document, PyCDocumentDto
from .embedding import embed_sentence


async def read_file(file: UploadFile) -> Tuple[str, int]:
    contents = await file.read()
    file_size = os.fstat(file.file.fileno()).st_size
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension == "pdf":
        pdf_reader = PdfReader(io.BytesIO(contents))
        str_content = ""
        for page in pdf_reader.pages:
            str_content += page.extract_text()

    elif file_extension == "docx":
        doc = docx.Document(io.BytesIO(contents))
        str_content = ""
        for para in doc.paragraphs:
            str_content += para.text

    else:
        str_content = contents.decode("utf-8")

    return str_content, file_size


def split_content(str_content: str, chunk_size: int = 300) -> List[Document]:
    docs = []
    index = 0

    while str_content:
        chunk = str_content[:chunk_size]
        str_content = str_content[chunk_size:]
        doc = Document(index=index, document=chunk)
        docs.append(doc)
        index += 1

    return docs


def embed_documents(documents: List[Document]) -> Tuple[List[Document], float]:
    embed_times = []

    for document in documents:
        doc_start_time = time.time()
        emb = embed_sentence(sentence=document.document)
        document.embedding = emb
        doc_end_time = time.time()
        doc_embed_time = doc_end_time - doc_start_time
        embed_times.append(doc_embed_time)
        logging.info("embedding completed, (%s/%s)", document.index + 1, len(documents))

    avg_embed_time = sum(embed_times) / len(embed_times) if embed_times else 0.0

    return documents, round(avg_embed_time, 3)


def encrypt_documents(documents: List[Document]) -> Tuple[List[PyCDocumentDto], float]:
    encrypted_documents = []
    encrypt_times = []

    for document in documents:
        doc_start_time = time.time()
        enc_doc = _encrypt_document(document.document)
        enc_emb = _encrypt_embedding(document.embedding)
        doc_end_time = time.time()
        doc_encrypt_time = doc_end_time - doc_start_time
        encrypt_times.append(doc_encrypt_time)

        encrypted_document = PyCDocumentDto(
            index=document.index,
            document=base64.b64encode(enc_doc.to_bytes()).decode("utf-8"),
            embedding=base64.b64encode(enc_emb.to_bytes()).decode("utf-8"),
        )

        encrypted_documents.append(encrypted_document)

    avg_encrypt_time = sum(encrypt_times) / len(encrypt_times) if encrypt_times else 0.0

    return encrypted_documents, round(avg_encrypt_time, 3)


def send_documents(uri: str, encrypted_documents: List[PyCDocumentDto]):
    load_dotenv()

    server_url = os.getenv("SERVER_URL") or "EMPTY"

    json = [doc.to_dict() for doc in encrypted_documents]
    response = requests.post(server_url + uri, json=json, timeout=9)

    return response


def _encrypt_document(document: str) -> PyCtxt:
    emb = _string_to_numpy(document)

    return _encrypt_embedding(emb)


def _encrypt_embedding(embedding: np.ndarray) -> PyCtxt:
    he = load_he_from_key()

    n_slots = he.get_nSlots()
    ctxt = [he.encrypt(embedding[j : j + n_slots]) for j in range(0, len(embedding), n_slots)]

    return ctxt[0]


def _string_to_numpy(str_to_convert: str) -> np.ndarray:
    arr_str = np.array([ord(c) for c in str_to_convert], dtype=np.float64)
    return arr_str
