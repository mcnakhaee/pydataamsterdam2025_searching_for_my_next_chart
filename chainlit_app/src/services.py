import requests
import json
from openai import OpenAI
from rag.weaviate_client import WeaviateClient
from rag.retriever import Retriever
from modules.image_utils import process_image_bytes, image_bytes_to_base64
from prompts.image_prompts import IMAGE_PROMPT

def get_openai_client(api_key, base_url):
    return OpenAI(api_key=api_key, base_url=base_url)

def get_weaviate_client():
    return WeaviateClient()

def get_retriever(client, collection_name, properties, vector):
    return Retriever(client=client, collection_name=collection_name, return_properties=properties, target_vector=vector)

async def analyze_image(client, img_base64: str, prompt: str, model: str = "moonshot-v1-8k-vision-preview"):
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                {"type": "text", "text": prompt}
            ]
        }]
    )
    return response.choices[0].message.content

async def process_uploaded_image(client, image_file):
    try:
        image_content = process_image_bytes(image_file.content)
        img_base = image_bytes_to_base64(image_content)
        description = await analyze_image(client, img_base, IMAGE_PROMPT)
        return description
    except Exception as e:
        print(f"Error processing image with OpenAI: {e}")
        return None

async def process_image_from_url(client, image_url: str):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_content = process_image_bytes(response.content)
        img_base = image_bytes_to_base64(image_content)
        description = await analyze_image(client, img_base, IMAGE_PROMPT)
        return description
    except Exception as e:
        print(f"Error processing image from URL: {e}")
        return None