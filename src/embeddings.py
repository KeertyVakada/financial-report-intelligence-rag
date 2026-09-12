import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CHUNKS_PATH = "../data/processed/chunks.json"
EMBEDDINGS_PATH = "../data/processed/embeddings.npy"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


# ---------------------------------------------------------
# 1. Load chunks
# ---------------------------------------------------------

print("Loading chunks...")

chunks_path = Path(CHUNKS_PATH)

if not chunks_path.exists():
    raise FileNotFoundError(
        f"Chunks file not found: {chunks_path}"
    )

with open(
    chunks_path,
    "r",
    encoding="utf-8",
) as file:
    chunks = json.load(file)

print(f"Loaded {len(chunks)} chunks.")


# ---------------------------------------------------------
# 2. Load embedding model
# ---------------------------------------------------------

print("\nLoading embedding model...")
print(f"Model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# ---------------------------------------------------------
# 3. Prepare text
# ---------------------------------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]

print(f"\nPreparing {len(texts)} texts for embedding...")


# ---------------------------------------------------------
# 4. Generate embeddings
# ---------------------------------------------------------

print("Generating embeddings...")

embeddings = model.encode(
    texts,
    batch_size=16,
    show_progress_bar=True,
    normalize_embeddings=True,
)

embeddings = np.asarray(
    embeddings,
    dtype=np.float32,
)


# ---------------------------------------------------------
# 5. Validate embeddings
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("EMBEDDING VALIDATION")
print("=" * 60)

print(f"Number of embeddings : {embeddings.shape[0]}")
print(f"Embedding dimensions : {embeddings.shape[1]}")
print(f"Data type            : {embeddings.dtype}")


# ---------------------------------------------------------
# 6. Verify chunk/vector alignment
# ---------------------------------------------------------

if embeddings.shape[0] != len(chunks):
    raise ValueError(
        "Number of embeddings does not match "
        "number of chunks."
    )

print(
    "Chunk/vector alignment: OK"
)


# ---------------------------------------------------------
# 7. Save embeddings
# ---------------------------------------------------------

embeddings_path = Path(EMBEDDINGS_PATH)

embeddings_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

np.save(
    embeddings_path,
    embeddings,
)


# ---------------------------------------------------------
# 8. Final confirmation
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("EMBEDDINGS SAVED SUCCESSFULLY")
print("=" * 60)

print(f"Output file          : {embeddings_path}")
print(f"Total embeddings     : {len(embeddings)}")
print(f"Vector dimensions    : {embeddings.shape[1]}")
print(f"Embedding file size  : {embeddings_path.stat().st_size / 1024:.2f} KB")