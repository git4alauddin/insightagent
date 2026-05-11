import hashlib
import math
import re

from app.config import settings
from app.schemas.document import DocumentChunk


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


class DocumentEmbeddingError(Exception):
    pass


def generate_embedding(text: str, dimensions: int | None = None) -> list[float]:
    resolved_dimensions = (
        settings.document_embedding_dimensions
        if dimensions is None
        else dimensions
    )
    _validate_dimensions(resolved_dimensions)

    tokens = TOKEN_PATTERN.findall(text.lower())
    if not tokens:
        raise DocumentEmbeddingError("Text must contain at least one token.")

    vector = [0.0] * resolved_dimensions
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], byteorder="big") % resolved_dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    return _normalize_vector(vector)


def generate_chunk_embeddings(
    chunks: list[DocumentChunk],
    dimensions: int | None = None,
) -> dict[str, list[float]]:
    return {
        chunk.chunk_id: generate_embedding(chunk.text, dimensions=dimensions)
        for chunk in chunks
    }


def _validate_dimensions(dimensions: int) -> None:
    if dimensions <= 0:
        raise DocumentEmbeddingError("Embedding dimensions must be greater than 0.")


def _normalize_vector(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        raise DocumentEmbeddingError("Embedding vector magnitude cannot be zero.")

    return [value / magnitude for value in vector]
