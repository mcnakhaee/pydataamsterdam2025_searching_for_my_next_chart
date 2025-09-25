import openai
from weaviate.classes.query import MetadataQuery

class Retriever:
    def __init__(self, client, collection_name="dviz_c_structured_v3", return_properties=None, target_vector=None):
        self.client = client  # This is your WeaviateClient wrapper
        self.collection_name = collection_name
        self.return_properties = return_properties or ["image_url", "section_11_description"]
        self.target_vector = target_vector
        
    def retrieve(self, query_text, limit=15, filters=None):
        # Call the wrapper method, not the direct client
        return self.client.query_near_text(
            query_text=query_text,
            collection_name=self.collection_name,
            limit=limit,
            target_vector=self.target_vector,
            return_metadata=MetadataQuery(distance=True),
            return_properties=self.return_properties,
            filters=filters
        )

    def hybrid_retrieve(self, query_text, limit=15, alpha=0.5, filters=None):
        # Call the wrapper method, not the direct client
        return self.client.query_hybrid(
            query_text=query_text,
            collection_name=self.collection_name,
            limit=limit,
            alpha=alpha,
            target_vector=self.target_vector,
            return_metadata=MetadataQuery(score=True),
            return_properties=self.return_properties,
            filters=filters
        )