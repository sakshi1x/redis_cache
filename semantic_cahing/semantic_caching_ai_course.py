import redis
import openai
import numpy as np


# in course, vectors are stores in hasehs or json . You also create a vector index using either:

# FLAT (brute-force search; best for small datasets)

# HNSW (Hierarchical Navigable Small World graph; faster for large datasets)

# Run vector similarity search
# You take your query, embed it into a vector with the same model, and then Redis finds the vectors most similar to your query vector using distance metrics:

# COSINE → measures angle between vectors (good for semantic meaning)

# L2 → Euclidean distance

# IP → inner product
# --- CONFIG ---
openai.api_key = "YOUR_OPENAI_KEY"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
INDEX_NAME = "hybrid_idx"
VECTOR_DIM = 1536

# --- CONNECT ---
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

# --- CREATE INDEX ---
try:
    r.execute_command(f"FT.DROPINDEX {INDEX_NAME} DD")
except redis.ResponseError:
    pass

r.execute_command(f"""
FT.CREATE {INDEX_NAME} ON JSON PREFIX 1 doc:
SCHEMA
$.content AS content TEXT
$.genre AS genre TAG
$.embedding AS embedding VECTOR HNSW 6 TYPE FLOAT32 DIM {VECTOR_DIM} DISTANCE_METRIC COSINE
""")

# --- STORE DOCUMENTS ---
data = [
    {"content": "That is a happy dog", "genre": "pets"},
    {"content": "A cute cat playing with yarn", "genre": "pets"},
    {"content": "The stock market is volatile today", "genre": "finance"},
]

for i, doc in enumerate(data, start=1):
    embedding = openai.Embedding.create(model="text-embedding-ada-002", input=doc["content"])["data"][0]["embedding"]
    r.json().set(f"doc:{i}", "$", {
        "content": doc["content"],
        "genre": doc["genre"],
        "embedding": np.array(embedding, dtype=np.float32).tobytes()
    })

# --- QUERY ---
query_text = "A joyful puppy"
query_embedding = openai.Embedding.create(model="text-embedding-ada-002", input=query_text)["data"][0]["embedding"]
query_vec = np.array(query_embedding, dtype=np.float32).tobytes()

results = r.execute_command(
    "FT.SEARCH", INDEX_NAME,
    "@genre:{pets}=>[KNN 2 @embedding $vec AS score]",
    "RETURN", 3, "content", "genre", "score",
    "SORTBY", "score", "ASC",
    "DIALECT", 2,
    "PARAMS", 2, "vec", query_vec
)

print("\nHybrid Semantic Search Results:\n", results)
