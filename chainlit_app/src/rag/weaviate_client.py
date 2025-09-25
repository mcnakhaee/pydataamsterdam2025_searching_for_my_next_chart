    # ...existing __init__ and get_collection...
import os
import weaviate
from dotenv import load_dotenv
import re
import urllib.parse
load_dotenv()
from app_config import WEAVIATE_CLOUD_URL, WEAVIATE_CLUSTER_API_KEY, WEAVIATE_COLLECTION_NAME, Mistral_API_KEY

class WeaviateClient:
    def __init__(self):
        print(f"Using Weaviate client version: {weaviate.__version__}")
        weaviate_url = WEAVIATE_CLOUD_URL
        weaviate_api_key = WEAVIATE_CLUSTER_API_KEY
        headers = {}
        if Mistral_API_KEY:
            headers["X-Mistral-Api-Key"] = Mistral_API_KEY

        self.client = weaviate.connect_to_wcs(
            cluster_url=weaviate_url,
            auth_credentials=weaviate.AuthApiKey(weaviate_api_key),
            headers=headers
        )
        print(f"Successfully connected to Weaviate at {weaviate_url}")

    def get_collection(self, collection_name=WEAVIATE_COLLECTION_NAME):
        return self.client.collections.get(collection_name)

    def query_near_text(
        self,
        query_text,
        collection_name=WEAVIATE_COLLECTION_NAME,
        limit=15,
        return_properties=None,
        return_metadata=None,
        target_vector=None,
        filters = None
    ):
        collection = self.get_collection(collection_name)
        return collection.query.near_text(
            query=query_text,
            limit=limit,
            return_properties=return_properties,
            return_metadata=return_metadata,
            target_vector=target_vector,
            filters=filters
        )

    def query_hybrid(
        self,
        query_text,
        collection_name=WEAVIATE_COLLECTION_NAME,
        limit=15,
        alpha=0.5,
        return_properties=None,
        return_metadata=None,
        target_vector=None,
        filters = None
    ):
        collection = self.get_collection(collection_name)
        return collection.query.hybrid(
            query=query_text,
            limit=limit,
            alpha=alpha,
            return_properties=return_properties,
            return_metadata=return_metadata,
            target_vector=target_vector,
            filters=filters
        )

    def query_near_vector(
        self,
        near_vector,
        collection_name=WEAVIATE_COLLECTION_NAME,
        limit=15,
        target_vector=None,
        return_metadata=None,
        return_properties=None,
        filters = None
    ):
        collection = self.get_collection(collection_name)
        return collection.query.near_vector(
            near_vector=near_vector,
            limit=limit,
            target_vector=target_vector,
            return_metadata=return_metadata,
            return_properties=return_properties,
            filters=filters

        )

    @property
    def collections(self):
        return self.client.collections