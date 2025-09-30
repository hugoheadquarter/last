from utils.claude_client import ClaudeClient
from utils.seedream_client import SeedreamClient
from models.data_models import LyricLine, StyleGuide, GeneratedImage, ImagePromptDecision
from typing import List, Optional
from pathlib import Path
from config.settings import config
import time
from tqdm import tqdm

class ImageDirector:
    def __init__(self):
        self.claude = ClaudeClient()
        self.seedream = SeedreamClient()
    
    def generate_all_images(self, target_lyrics: List[LyricLine],
                           style_guide: StyleGuide,
                           song_id: str) -> List[GeneratedImage]:
        """Generate all images for the lyric lines"""
        
        generated_images = []
        previous_image_path = None
        previous_prompt = None
        
        # Create output directory for this song
        frames_dir = config.FRAMES_DIR / song_id
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, lyric in enumerate(tqdm(target_lyrics, desc="Generating images")):
            print(f"\n🎨 Generating image for Line {lyric.line_number}: {lyric.english_text}")
            
            start_time = time.time()
            
            if idx == 0:
                # First image - no reference
                print("  → Creating first image (no reference)")
                prompt = self.claude.generate_first_prompt(
                    lyric.dict(),
                    style_guide.dict()
                )
                use_reference = False
            else:
                # Subsequent images - use previous as reference
                print(f"  → Creating image with reference to line {target_lyrics[idx-1].line_number}")
                decision = self.claude.generate_next_prompt(
                    previous_prompt,
                    lyric.dict(),
                    style_guide.dict()
                )
                prompt = decision['seedream_prompt']
                use_reference = decision['use_previous_as_reference']
                print(f"  → Reasoning: {decision['creative_reasoning']}")
            
            # Generate image
            print(f"  → Calling Seedream API...")
            result = self.seedream.generate_image(
                prompt=prompt,
                reference_image_path=previous_image_path if use_reference else None
            )
            
            # Download image
            image_url = result['data'][0]['url']
            image_filename = f"line_{lyric.line_number:03d}.jpg"
            image_path = frames_dir / image_filename
            
            self.seedream.download_image(image_url, image_path)
            
            generation_time = time.time() - start_time
            print(f"  ✓ Generated in {generation_time:.2f}s → {image_path}")
            
            # Store metadata
            generated_images.append(GeneratedImage(
                line_number=lyric.line_number,
                image_path=str(image_path),
                prompt_used=prompt,
                start_time=lyric.start_time_seconds,
                end_time=lyric.end_time_seconds,
                used_reference=use_reference,
                reference_image=str(previous_image_path) if previous_image_path else None,
                generation_time=generation_time
            ))
            
            # Update state for next iteration
            previous_image_path = image_path
            previous_prompt = prompt
            
            # Rate limiting
            time.sleep(1)
        
        return generated_images