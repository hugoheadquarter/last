from utils.claude_client import ClaudeClient
from utils.seedream_client import SeedreamClient
from agents.reference_selector import ReferenceSelector
from utils.generation_logger import GenerationLogger
from models.data_models import LyricLine, StyleGuide, GeneratedImage
from typing import List, Optional
from pathlib import Path
from config.settings import config
import time
from tqdm import tqdm

class ImageDirector:
    def __init__(self):
        self.claude = ClaudeClient()
        self.seedream = SeedreamClient()
        self.reference_selector = ReferenceSelector()
    
    def generate_character_designs(self, style_guide: StyleGuide, song_id: str) -> List[Path]:
        """Generate character design references (male and female portraits)"""
        print("\n🎨 GENERATING CHARACTER DESIGNS...")
        
        frames_dir = config.FRAMES_DIR / song_id
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        character_refs = []
        
        # Generate male character
        print("  → Generating male character design...")
        male_prompt = self.claude.generate_character_design(
            style_guide.dict(),
            gender="male"
        )
        print(f"  Prompt: {male_prompt[:100]}...")
        
        male_result = self.seedream.generate_image(
            prompt=male_prompt,
            reference_image_paths=None
        )
        
        male_url = male_result['data'][0]['url']
        male_path = frames_dir / "character_male.jpg"
        self.seedream.download_image(male_url, male_path)
        character_refs.append(male_path)
        print(f"  ✓ Male character saved: {male_path}")
        
        time.sleep(2)  # Rate limiting
        
        # Generate female character
        print("  → Generating female character design...")
        female_prompt = self.claude.generate_character_design(
            style_guide.dict(),
            gender="female"
        )
        print(f"  Prompt: {female_prompt[:100]}...")
        
        female_result = self.seedream.generate_image(
            prompt=female_prompt,
            reference_image_paths=None
        )
        
        female_url = female_result['data'][0]['url']
        female_path = frames_dir / "character_female.jpg"
        self.seedream.download_image(female_url, female_path)
        character_refs.append(female_path)
        print(f"  ✓ Female character saved: {female_path}")
        
        print(f"\n✓ Character designs complete: {len(character_refs)} references created\n")
        
        return character_refs
    
    def generate_all_images(self, target_lyrics: List[LyricLine],
                           style_guide: StyleGuide,
                           song_id: str) -> List[GeneratedImage]:
        """Generate all images for the lyric lines"""
        
        generated_images = []
        previous_prompts = []
        
        frames_dir = config.FRAMES_DIR / song_id
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        log_path = config.VIDEOS_DIR / f"generation_log_{song_id}.txt"
        logger = GenerationLogger(log_path)
        logger.log_style_guide(style_guide.dict())
        
        # STEP 1: Generate character designs
        character_refs = self.generate_character_designs(style_guide, song_id)
        logger.log("\n=== CHARACTER DESIGNS GENERATED ===")
        logger.log(f"Male: {character_refs[0]}")
        logger.log(f"Female: {character_refs[1]}\n")
        
        total_lines = len(target_lyrics)
        pipeline_start = time.time()
        
        # STEP 2: Generate line images (all use character refs)
        for idx, lyric in enumerate(tqdm(target_lyrics, desc="Generating images")):
            print(f"\n🎨 Generating image for Line {lyric.line_number}: {lyric.english_text}")
            
            logger.log_line_start(lyric.line_number, lyric.english_text, lyric.korean_text)
            
            start_time = time.time()
            
            if idx == 0:
                # First image
                print("  → Creating first image with character references")
                prompt = self.claude.generate_first_prompt(
                    lyric.dict(),
                    style_guide.dict()
                )
                logger.log_prompt_generation(prompt)
                
            else:
                # Subsequent images
                print(f"  → Creating image {idx+1} with character references")
                decision = self.claude.generate_next_prompt(
                    previous_prompts,
                    lyric.dict(),
                    style_guide.dict(),
                    line_number=lyric.line_number,
                    total_lines=total_lines
                )
                prompt = decision['seedream_prompt']
                reasoning = decision['creative_reasoning']
                
                print(f"  → Reasoning: {reasoning[:150]}...")
                logger.log_prompt_generation(prompt, reasoning)
            
            # Always use character references (never previous line images)
            print(f"  → Using character design references")
            logger.log(f"  Reference: Character designs (male + female portraits)\n")
            
            # Generate image
            print(f"  → Calling Seedream API...")
            try:
                result = self.seedream.generate_image(
                    prompt=prompt,
                    reference_image_paths=character_refs  # Always use character designs
                )
                
                # Download image
                image_url = result['data'][0]['url']
                image_filename = f"line_{lyric.line_number:03d}.jpg"
                image_path = frames_dir / image_filename
                
                self.seedream.download_image(image_url, image_path)
                
                generation_time = time.time() - start_time
                print(f"  ✓ Generated in {generation_time:.2f}s → {image_path}")
                
                logger.log_generation_result(True, generation_time, str(image_path))
                
                # Store metadata
                generated_images.append(GeneratedImage(
                    line_number=lyric.line_number,
                    image_path=str(image_path),
                    prompt_used=prompt,
                    start_time=lyric.start_time_seconds,
                    end_time=lyric.end_time_seconds,
                    used_reference=True,
                    reference_image=str(character_refs),
                    generation_time=generation_time
                ))
                
                # Add to prompt history (but NOT to reference history)
                previous_prompts.append(prompt)
                
            except Exception as e:
                logger.log_generation_result(False, time.time() - start_time, f"ERROR: {str(e)}")
                raise
            
            time.sleep(1)
        
        # Log final summary
        total_time = time.time() - pipeline_start
        logger.log_summary(len(generated_images), total_time)
        
        print(f"\n📝 Generation log saved to: {log_path}")
        
        return generated_images