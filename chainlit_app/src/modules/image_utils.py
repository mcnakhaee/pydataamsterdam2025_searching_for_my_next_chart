import re
import io
import base64
from PIL import Image

def convert_github_url_to_raw(github_url: str) -> str:
    """Convert GitHub repository URL to raw content URL for images."""
    github_pattern = r'https://github\.com/([^/]+)/([^/]+)/blob/(.+)'
    match = re.match(github_pattern, github_url)
    if match:
        user, repo, path = match.groups()
        return f'https://raw.githubusercontent.com/{user}/{repo}/{path}'
    return github_url

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
