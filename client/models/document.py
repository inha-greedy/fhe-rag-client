import base64

from Pyfhel import PyCtxt, Pyfhel
from pydantic import BaseModel, Field
import numpy as np


class Document(BaseModel):
    index: int
    document: str
    embedding: np.ndarray = Field(default_factory=lambda: np.zeros(3))

    class Config:
        arbitrary_types_allowed = True


class PyCDocument(BaseModel):
    index: int
    document: PyCtxt = Field(default_factory=PyCtxt())
    embedding: PyCtxt = Field(default_factory=PyCtxt())

    class Config:
        arbitrary_types_allowed = True


class PyCDocumentDto(BaseModel):
    index: int
    document: str
    embedding: str

    def to_dict(self):
        return {
            "index": self.index,
            "document": self.document,
            "embedding": self.embedding,
        }

    def to_document(self, he: Pyfhel):
        index = self.index
        document = PyCtxt(pyfhel=he, bytestring=base64.b64decode(self.document))
        embedding = PyCtxt(pyfhel=he, bytestring=base64.b64decode(self.embedding))

        return PyCDocument(index=index, document=document, embedding=embedding)
