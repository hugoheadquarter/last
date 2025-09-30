import requests
import base64
from pathlib import Path
from config.settings import config
from typing import Optional, List
import time

class SeedreamClient:
    def __init__(self):
        self.api_key = config.SEEDREAM_API_KEY
        self.endpoint = config.SEEDREAM_ENDPOINT
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_image(self, prompt: str, 
                      reference_image_paths: Optional[List[Path]] = None,
                      size: str = "1080x1080") -> dict:
        """Generate image with Seedream API supporting up to 10 reference images"""
        
        # Build negative prompt to prevent unwanted elements
        negative_prompt = (
            "text overlay, korean text, english text, "
            "subtitles, words, letters, captions, typography"
        )
        
        payload = {
            "model": "seedream-4-0-250828",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "size": size,
            "sequential_image_generation": "disabled",
            "response_format": "url",
            "watermark": False,
            "stream": False
        }
        
        # Add multiple reference images if provided (max 10)
        if reference_image_paths and len(reference_image_paths) > 0:
            try:
                images_data = []
                
                # Filter valid paths and limit to 10
                valid_paths = [p for p in reference_image_paths if p.exists()][:10]
                
                for img_path in valid_paths:
                    with open(img_path, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                        
                        # Determine image format
                        ext = img_path.suffix.lower().replace('.', '')
                        if ext == 'jpg':
                            ext = 'jpeg'
                        
                        images_data.append(f"data:image/{ext};base64,{img_data}")
                
                if len(images_data) > 0:
                    # Seedream expects string for 1 image, array for multiple
                    if len(images_data) == 1:
                        payload["image"] = images_data[0]
                    else:
                        payload["image"] = images_data
                    
                    print(f"  → Using {len(images_data)} reference image(s) for style consistency")
                    
            except Exception as e:
                print(f"  ⚠️  Could not load reference images: {e}")
                # Continue without reference
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Seedream API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"  Error details: {error_detail}")
                except:
                    print(f"  Response text: {e.response.text[:200]}")
            raise
    
    def download_image(self, url: str, output_path: Path) -> Path:
        """Download generated image from URL"""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
            
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Image download error: {e}")
            raise