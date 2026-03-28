import base64
import requests
from io import BytesIO
from pathlib import Path

class ImageHelper:
    @staticmethod
    def encode_image(image_source: str) -> str:
        """
        Converts a local path or a URL into a base64 string.
        """
        try:
            # Case 1: Online Image URL
            if image_source.startswith(("http://", "https://")):
                response = requests.get(image_source)
                response.raise_for_status()
                binary_data = response.content
            
            # Case 2: Local Downloaded Image
            else:
                image_path = Path(image_source)
                if not image_path.exists():
                    return "Error: File not found"
                with open(image_path, "rb") as image_file:
                    binary_data = image_file.read()

            # Encode to Base64
            base64_encoded = base64.b64encode(binary_data).decode('utf-8')
            
            # Optional: Add Data URI header (useful for frontend <img> tags)
            # return f"data:image/jpeg;base64,{base64_encoded}"
            return base64_encoded

        except Exception as e:
            return f"Error: {str(e)}"