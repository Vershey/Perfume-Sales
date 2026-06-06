"""
ingest.py  —  Build the multimodal index from market-report PDFs.

For every PDF page we:
  1. extract the raw text (PyMuPDF),
  2. render the page to a PNG and ask Claude (vision) to read any
     charts/tables and write out the numbers as plain text,
  3. combine text + visual reading, chunk it, embed locally, and store
     it in Chroma with metadata (source file, page, the page image path).

The stored page-image paths let query.py re-send the *actual* charts to
Claude at answer time — that's the "multimodal" part on both ends.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python ingest.py          # ingests every *.pdf in ./data
"""
import glob
import os

import anthropic
import fitz  # PyMuPDF

import config
import utils

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

VISION_PROMPT = (
    "You are reading one page of a fragrance/perfume market-research report. "
    "If the page contains any CHARTS, GRAPHS, or TABLES, transcribe their data "
    "into clear plain text: state the chart title, the metric and units (e.g. "
    "USD billion), every axis label, and each data point or row you can read "
    "(year -> value, region -> share %, segment -> value, etc.). Note the CAGR "
    "and the source/publisher if shown. If the page has no figures, reply with "
    "exactly: NO_FIGURES. Do not add commentary or interpretation."
)


def read_visuals(image_path: str) -> str:
    """Ask Claude to transcribe charts/tables on a page image."""
    msg = client.messages.create(
        model=config.VISION_MODEL,
        max_tokens=config.MAX_TOKENS,
        messages=[{
            "role": "user",
            "content": [utils.image_block(image_path),
                        {"type": "text", "text": VISION_PROMPT}],
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    return "" if text == "NO_FIGURES" else text


def ingest_pdf(pdf_path: str, collection):
    source = os.path.basename(pdf_path)
    doc = fitz.open(pdf_path)
    print(f"\n=== {source}  ({doc.page_count} pages) ===")

    ids, docs, metas, embeds = [], [], [], []

    for i, page in enumerate(doc):
        page_text = page.get_text().strip()

        img_name = f"{os.path.splitext(source)[0]}_p{i+1}.png"
        img_path = os.path.join(config.PAGE_IMAGE_DIR, img_name)
        utils.render_page_to_png(page, img_path)

        visual_text = read_visuals(img_path)
        if visual_text:
            print(f"  page {i+1}: read figures ({len(visual_text)} chars)")

        combined = page_text
        if visual_text:
            combined += f"\n\n[FIGURE DATA — read from charts/tables on this page]\n{visual_text}"

        for j, chunk in enumerate(utils.chunk_text(combined)):
            ids.append(f"{source}-p{i+1}-c{j}")
            docs.append(chunk)
            metas.append({"source": source, "page": i + 1, "image_path": img_path,
                          "has_figure": bool(visual_text)})

    if not docs:
        print("  (no extractable text)")
        return

    # Embed in batches and store.
    embeds = utils.embed(docs)
    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeds)
    print(f"  stored {len(docs)} chunks")


def main():
    utils.ensure_dirs()
    pdfs = sorted(glob.glob(os.path.join(config.DATA_DIR, "*.pdf")))
    if not pdfs:
        print(f"No PDFs found in ./{config.DATA_DIR}. Drop market-report PDFs there first.")
        return

    collection = utils.get_collection()
    for pdf in pdfs:
        ingest_pdf(pdf, collection)

    print(f"\nDone. Collection now holds {collection.count()} chunks.")
    print("Run:  python query.py \"What was the global perfume market size by year?\"")


if __name__ == "__main__":
    main()
