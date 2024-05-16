import base64

from Pyfhel import PyCtxt
from pydantic import BaseModel, Field

from ..services.enc import get_he_context


class Similarity(BaseModel):
    index: int
    score: float


class PyCSimilarity(BaseModel):
    index: int
    score: PyCtxt = Field(default_factory=PyCtxt())

    class Config:
        arbitrary_types_allowed = True


class PyCSimilarityDto(BaseModel):

    index: int
    score: str

    def to_dict(self):

        return {
            "index": self.index,
            "score": self.score,
        }

    def to_similarity(self):
        he = get_he_context()

        index = self.index
        score = PyCtxt(pyfhel=he, bytestring=base64.b64decode(self.score))

        return PyCSimilarity(index=index, score=score)
