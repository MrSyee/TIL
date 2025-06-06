# %%
from pymilvus import connections, Collection, FieldSchema, DataType, CollectionSchema
from pymilvus import utility
# %%
# Create client
print("Create client")
connections.connect(alias="default", host="localhost", port="19530")

# Create collection
collection_name = "demo_collection"

# Delete collection if it exists
if utility.has_collection(collection_name):
    print("Delete collection")
    utility.drop_collection(collection_name)

print("Create collection")
s_id = FieldSchema(
  name="s_id",
  dtype=DataType.INT64,
  is_primary=True,
)
sentence_vector = FieldSchema(
  name="sentence_vector",
  dtype=DataType.FLOAT_VECTOR,
  dim=768,
)
sentence = FieldSchema(
  name="sentence",
  dtype=DataType.VARCHAR,
  max_length=100,
)
schema = CollectionSchema(
  fields=[s_id, sentence, sentence_vector],
  description="Test sentence search"
)

collection = Collection(
    name="demo_collection",
    schema=schema,
    using='default',
    shards_num=2,
    consistency_level="Strong"
)

index_params = {
  "metric_type":"L2",
  "index_type":"IVF_FLAT",
  "params":{"nlist":1024}
}

collection.create_index(
  field_name="sentence_vector",
  index_params=index_params
)

# %%
# Prepare Data
from pymilvus import model

# This will download a small embedding model "paraphrase-albert-small-v2" (~50MB).
embedding_fn = model.DefaultEmbeddingFunction()

# Text strings to search from.
docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
]

vectors = embedding_fn.encode_documents(docs)
# The output vector has 768 dimensions, matching the collection that we just created.
print("Dim:", embedding_fn.dim, vectors[0].shape)  # Dim: 768 (768,)


# %%
# Each entity has id, vector representation, raw text, and a subject label that we use
# to demo metadata filtering later.
data = [
    {"s_id": i, "sentence": docs[i], "sentence_vector": vectors[i]}
    for i in range(len(vectors))
]

print("Data has", len(data), "entities, each with fields: ", data[0].keys())
print("Vector dim:", len(data[0]["sentence_vector"]))


# %%
# Insert data
res = collection.insert(data)

print("Insert data: ", res)

# %%
# Load collection into memory before searching
print("Loading collection...")
collection.load()


# %%
# Semantic Serach: Vector Search
query_vectors = embedding_fn.encode_queries(["Who is Alan Turing?"])

search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

res = collection.search(
    data=query_vectors,  # query vectors
    anns_field="sentence_vector",
    param=search_params,
    limit=2,  # number of returned entities
    output_fields=["s_id", "sentence", "sentence_vector"],  # specifies fields to be returned
)

for hit in res[0]:
    print(hit.id)
    print(hit.entity.s_id)
    print(hit.entity.sentence)
    print(hit.entity.sentence_vector)
    print(hit.distance)
    print("-"*100)

# %%
