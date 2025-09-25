import requests
import base64
import io
from PIL import Image

# Add this to your imports
prompt_img = "Analyze this data visualization and provide a detailed description of what it shows, including chart type, data patterns, visual elements, and key insights."

def process_image_bytes(image_bytes: bytes) -> bytes:
    """Convert image bytes to RGB JPEG bytes."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode in ['P', 'RGBA', 'LA']:
        if image.mode == 'P':
            image = image.convert('RGB')
        else:
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1])
            image = rgb_image
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=95)
    return img_byte_arr.getvalue()

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

async def analyze_image_with_llm(client, img_base64: str, prompt: str):
    response = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content

def process_image_from_url(image_url: str, prompt: str):
    """Process image from URL and analyze with LLM"""
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    
    image_content = process_image_bytes(response.content)
    img_base64 = image_bytes_to_base64(image_content)
    description = analyze_image_with_llm(client, img_base64, prompt)
    return description


