"""
Central configuration for the multimodal perfume-market RAG pipeline.
Tweak these without touching the pipeline code.
"""

# --- Anthropic models ---------------------------------------------------
# Current IDs (June 2026). Swap GEN_MODEL to "claude-opus-4-8" for the most
# capable (and more expensive) generation; Sonnet 4.6 is the cost/quality
# sweet spot and has strong vision.
VISION_MODEL = "claude-sonnet-4-6"   # used during ingestion to read charts/tables
GEN_MODEL = "claude-sonnet-4-6"      # used at query time to answer questions
MAX_TOKENS = 2048

# --- Embeddings (local, no API key needed) ------------------------------
# Anthropic has no embeddings endpoint, so we embed locally. all-MiniLM is
# small/fast and good enough for a demo. For better recall on long reports,
# try "BAAI/bge-base-en-v1.5".
EMBED_MODEL = "all-MiniLM-L6-v2"

# --- Paths --------------------------------------------------------------
DATA_DIR = "data"               # put your market-report PDFs here
PAGE_IMAGE_DIR = "page_images"  # rendered page PNGs (created automatically)
CHROMA_DIR = "chroma_db"        # persistent vector store

# --- Chunking / retrieval ----------------------------------------------
CHUNK_SIZE = 1000               # characters per chunk
CHUNK_OVERLAP = 200
TOP_K = 6                       # chunks retrieved per query
MAX_IMAGES_PER_ANSWER = 3       # source page images sent to the LLM at answer time
PAGE_RENDER_DPI = 130           # higher = sharper charts, bigger files/cost
MAX_IMAGE_EDGE = 1400           # px; Claude works best with images <~1568px long edge
