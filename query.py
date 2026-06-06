"""
query.py  —  Ask questions over the indexed perfume-market reports.

Retrieval is text-based (over both the page text and the chart/table data
Claude transcribed during ingestion). We then re-send the ACTUAL source
page images for the top hits to Claude, so it can answer by looking at the
charts directly — and we instruct it to cite sources and flag conflicting
numbers instead of silently averaging them.

Usage:
    python query.py "Which region grew fastest, and from which chart?"
    python query.py            # interactive mode
"""
import sys

import anthropic

import config
import utils

client = anthropic.Anthropic()

SYSTEM = (
    "You are a fragrance-market analyst. Answer ONLY from the retrieved text "
    "and the chart images provided. Rules:\n"
    "1. Attribute every figure to its source publisher/file when known.\n"
    "2. Market-size estimates vary by definition (fine fragrance vs all "
    "fragrance products). If sources disagree, present the RANGE and name who "
    "says what — never average them into one number silently.\n"
    "3. If a number comes from a chart, say which chart.\n"
    "4. If the answer isn't in the provided material, say so plainly.\n"
    "Be concise and quantitative."
)


def retrieve(question: str):
    collection = utils.get_collection()
    if collection.count() == 0:
        sys.exit("Index is empty. Run `python ingest.py` first.")
    q_emb = utils.embed([question])[0]
    res = collection.query(query_embeddings=[q_emb], n_results=config.TOP_K)
    return res["documents"][0], res["metadatas"][0]


def answer(question: str) -> str:
    docs, metas = retrieve(question)

    # Assemble retrieved text with source labels.
    context_blocks = []
    for d, m in zip(docs, metas):
        context_blocks.append(f"[{m['source']} p.{m['page']}]\n{d}")
    context = "\n\n---\n\n".join(context_blocks)

    # Collect up to N unique source page images (the charts themselves).
    seen, image_blocks = set(), []
    for m in metas:
        path = m.get("image_path")
        if m.get("has_figure") and path and path not in seen:
            seen.add(path)
            image_blocks.append(utils.image_block(path))
        if len(image_blocks) >= config.MAX_IMAGES_PER_ANSWER:
            break

    content = []
    if image_blocks:
        content.append({"type": "text",
                        "text": "Source chart/table pages referenced below:"})
        content.extend(image_blocks)
    content.append({"type": "text",
                    "text": f"Retrieved context:\n\n{context}\n\nQuestion: {question}"})

    msg = client.messages.create(
        model=config.GEN_MODEL,
        max_tokens=config.MAX_TOKENS,
        system=SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    out = "".join(b.text for b in msg.content if b.type == "text")
    sources = sorted({f"{m['source']} (p.{m['page']})" for m in metas})
    return out + "\n\nRetrieved from: " + "; ".join(sources)


def main():
    if len(sys.argv) > 1:
        print(answer(" ".join(sys.argv[1:])))
        return
    print("Interactive mode. Ctrl-C to quit.\n")
    while True:
        try:
            q = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q:
            print("\n" + answer(q) + "\n")


if __name__ == "__main__":
    main()
