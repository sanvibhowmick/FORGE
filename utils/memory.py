import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI

# Connection to the Qdrant service in your docker-compose
client = QdrantClient(url=os.getenv("QDRANT_URL", "http://127.0.0.1:6333"))
openai_client = OpenAI()

COLLECTION_NAME = "forge_repo_memory"
EMBEDDING_MODEL = "text-embedding-3-small"

def init_memory():
    """Sets up the vector collection if it doesn't exist."""
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        print(f"--- MEMORY: Creating fresh repository collection ---")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1536, # Standard for text-embedding-3-small
                distance=models.Distance.COSINE
            ),
        )

def ingest_directory(directory_path: str):
    """
    Scans an entire directory and stores every relevant file in Qdrant.
    Excludes .git, __pycache__, and venv to keep memory clean.
    """
    excluded_dirs = {'.git', '__pycache__', 'venv', 'node_modules'}
    
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.json')):
                file_path = os.path.join(root, file)
                _store_file_in_qdrant(file_path)

def _store_file_in_qdrant(file_path: str):
    """Internal helper to embed and upsert a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate the vector representation of the file content
    embedding = openai_client.embeddings.create(
        input=content,
        model=EMBEDDING_MODEL
    ).data[0].embedding

    # Use a hash of the path as a stable ID
    point_id = hash(file_path) % (10**8)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "content": content,
                    "type": "code" if file_path.endswith('.py') else "docs"
                }
            )
        ]
    )
    print(f"--- MEMORY: Ingested {file_path} ---")

def get_context(query: str, limit: int = 5):
    """Semantic search to find existing code/docs relevant to a new task."""
    query_embedding = openai_client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    ).data[0].embedding

    # NEW: Using the more stable query_points API
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    )
    
    # query_points returns a different object structure
    search_results = response.points

    context = []
    for res in search_results:
        # Check payload exists before accessing
        if res.payload:
            context.append(f"FILE: {res.payload.get('path', 'unknown')}\nCONTENT:\n{res.payload.get('content', '')}")
    
    return "\n\n---\n\n".join(context)