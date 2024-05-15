import os
from typing import List

import base64
import requests
from fastapi import UploadFile
from dotenv import load_dotenv

from ..models.document import Document, PyCDocumentDto
from .embedding import embed_sentence
from .enc import encrypt_document, encrypt_embedding


async def read_file(file: UploadFile) -> bytes:
    contents = await file.read()

    str_content = contents.decode("utf-8")

    return str_content


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


def embed_documents(documents: List[Document]) -> List[Document]:

    for document in documents:

        emb = embed_sentence(sentence=document.document)
        document.embedding = emb

    return documents


def encrypt_documents(documents: List[Document]) -> List[PyCDocumentDto]:

    encrypted_documents = []
    for document in documents:

        enc_doc = encrypt_document(document.document)
        enc_emb = encrypt_embedding(document.embedding)

        encrypted_document = PyCDocumentDto(
            index=document.index,
            document=base64.b64encode(enc_doc.to_bytes()).decode("utf-8"),
            embedding=base64.b64encode(enc_emb.to_bytes()).decode("utf-8"),
        )

        encrypted_documents.append(encrypted_document)

    return encrypted_documents


def send_documents_to_server(uri: str, encrypted_documents: List[PyCDocumentDto]):

    load_dotenv()

    server_url = os.getenv("SERVER_URL")
    server_url = "http://localhost:10100"

    json = [doc.to_dict() for doc in encrypted_documents]
    response = requests.post(server_url + uri, json=json)

    return response
