from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue


client = QdrantClient(url="http://localhost:6333")

# Search the nearest vectors to specific vector
print("Search the nearest vectors to specific vector")
search_result = client.query_points(
    collection_name="test_collection",
    query=[0.2, 0.1, 0.9, 0.7],
    with_payload=False,
    limit=3
).points

for r in search_result:
    print(dict(r))


# Search the nearest vectors with query filter
print("Search the nearest vectors with query filter")
search_result = client.query_points(
    collection_name="test_collection",
    query=[0.2, 0.1, 0.9, 0.7],
    query_filter=Filter(
        must=[FieldCondition(key="city", match=MatchValue(value="London"))]
    ),
    with_payload=True,
    limit=3,
).points

print(search_result)
