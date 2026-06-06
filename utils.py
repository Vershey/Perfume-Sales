"""
Shared helpers used by both ingest.py and query.py.
"""
import base64
import io
import os

import chromadb
import fitz  # PyMuPDF
from PIL import Image
from sentence_transformers import SentenceTransformer

import config

# ---------------------------------------------------------------------------
# Embeddings (loaded once, lazily)
# ---------------------------------------------------------------------------
_embedder = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(config.EMBED_MODEL)
    return _embedder


def embed(texts: list[str]) -> list[list[float]]:
    """Return embeddings for a list of strings."""
    vecs = get_embedder().encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
def get_collection():
    """Get (or create) the persistent Chroma collection."""
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return client.get_or_create_collection(
        name="perfume_market",
        metadata={"hnsw:space": "cosine"},
    )


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str) -> list[str]:
    """Simple character chunker with overlap."""
    text = text.strip()
    if not text:
        return []
    chunks, start = [], 0
    step = config.CHUNK_SIZE - config.CHUNK_OVERLAP
    while start < len(text):
        chunks.append(text[start : start + config.CHUNK_SIZE])
        start += step
    return chunks


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def render_page_to_png(page: "fitz.Page", out_path: str) -> str:
    """Render a PDF page to a downscaled PNG and return the path."""
    zoom = config.PAGE_RENDER_DPI / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

    # Downscale so the long edge fits Claude's recommended limit.
    long_edge = max(img.size)
    if long_edge > config.MAX_IMAGE_EDGE:
        scale = config.MAX_IMAGE_EDGE / long_edge
        img = img.resize((int(img.width * scale), int(img.height * scale)))

    img.save(out_path, "PNG")
    return out_path


def png_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def image_block(path: str) -> dict:
    """Build an Anthropic image content block from a PNG path."""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": png_to_base64(path),
        },
    }


def ensure_dirs():
    os.makedirs(config.PAGE_IMAGE_DIR, exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)
