import os
from dotenv import load_dotenv

load_dotenv()


MOONSHOT_BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
QWEN_VL_API_KEY = os.getenv("QWEN_VL_API_KEY", )
QWEB_VL_BASE_URL = os.getenv("QWEN_VL_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")#"
MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY')
# Environment variables
Mistral_API_KEY = os.getenv("Mistral_API_KEY")
WEAVIATE_CLOUD_URL = os.getenv("WEAVIATE_CLOUD_URL")
WEAVIATE_CLUSTER_API_KEY = os.getenv("WEAVIATE_CLUSTER_API_KEY") 
WEAVIATE_COLLECTION_NAME = "dviz_c_structured_v3"

COMMANDS = [
    {"id": "upload_image", "icon": "upload", "description": "Upload an image for analysis", "button": True, "persistent": False},
    {"id": "analyze_url", "icon": "link", "description": "Analyze image from URL", "button": True, "persistent": False},
    #{"id": "search_visualizations", "icon": "search", "description": "Search visualizations", "button": True, "persistent": False},
    #{"id": "clear_history", "icon": "trash-2", "description": "Clear history", "button": True, "persistent": False},
    {"id": "deconstruct_elements_tool", "icon": "search", "description": "Access tool functionalities", "button": True, "persistent": False},
    {"id": "hybrid_search", "icon": "layers", "description": "Perform a hybrid search", "button": True, "persistent": False},
    {"id": "long_context_retrieval", "icon": "list", "description": "Retrieve 100, rerank, show top 20", "button": True, "persistent": False},
]