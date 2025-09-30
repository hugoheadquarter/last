from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips
)
from models.data_models import GeneratedImage, LyricLine
from typing import List
from pathlib import Path
from config.settings import config
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from utils.text_utils import korean_to_romanization

# Fix for Pillow 10.0.0+ compatibility with MoviePy
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

class VideoCompositor:
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.image_size = config.IMAGE_SIZE
        self.fps = config.FPS
    
    def create_text_image(self, text: str, y_position: int) -> np.ndarray:
        """Create an image with text overlay"""
        # Create transparent image
        img = Image.new('RGBA', (self.width, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font
        font = ImageFont.truetype(str(config.FONT_PATH), config.FONT_SIZE)
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (self.width - text_width) // 2
        
        # Draw text
        draw.text((x_position, 10), text, font=font, fill=(255, 255, 255, 255))
        
        return np.array(img)
    
    def create_video_segment(self, image_data: GeneratedImage, 
                            lyric: LyricLine) -> CompositeVideoClip:
        """Create a single video segment with image and text"""
        duration = image_data.end_time - image_data.start_time
        
        # Load and resize image to square
        img_clip = (ImageClip(image_data.image_path)
                   .set_duration(duration)
                   .resize((self.image_size, self.image_size))
                   .set_position(('center', config.IMAGE_TOP_PADDING)))
        
        # Create black background
        bg_clip = (ImageClip(np.zeros((self.height, self.width, 3), dtype=np.uint8))
                  .set_duration(duration))
        
        # Create text clips
        english_clip = (ImageClip(self.create_text_image(lyric.english_text, 0))
                       .set_duration(duration)
                       .set_position(('center', config.TEXT_START_Y)))
        
        korean_clip = (ImageClip(self.create_text_image(lyric.korean_text, 0))
                      .set_duration(duration)
                      .set_position(('center', config.TEXT_START_Y + config.TEXT_SPACING)))
        
        # Get romanization using korean-romanizer
        romanization = korean_to_romanization(lyric.korean_text)
        roman_clip = (ImageClip(self.create_text_image(romanization, 0))
                     .set_duration(duration)
                     .set_position(('center', config.TEXT_START_Y + 2 * config.TEXT_SPACING)))
        
        # Composite all elements
        composite = CompositeVideoClip([
            bg_clip,
            img_clip,
            english_clip,
            korean_clip,
            roman_clip
        ], size=(self.width, self.height))
        
        return composite
    
    def assemble_video(self, images: List[GeneratedImage],
                      lyrics: List[LyricLine],
                      audio_path: Path,
                      output_path: Path) -> Path:
        """Assemble final video with all segments"""
        print("\n🎬 Assembling video...")
        
        # Create video segments
        segments = []
        for img_data in images:
            # Find corresponding lyric
            lyric = next(l for l in lyrics if l.line_number == img_data.line_number)
            segment = self.create_video_segment(img_data, lyric)
            segments.append(segment)
        
        # Concatenate all segments with crossfade
        print("  → Concatenating segments with transitions...")
        final_video = concatenate_videoclips(segments, method="compose")
        
        # Add audio
        print("  → Adding audio track...")
        audio = AudioFileClip(str(audio_path))
        
        # Trim audio to match video duration
        start_time = images[0].start_time
        end_time = images[-1].end_time
        audio_segment = audio.subclip(start_time, end_time)
        
        final_video = final_video.set_audio(audio_segment)
        
        # Export
        print(f"  → Exporting to {output_path}...")
        final_video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(config.TEMP_DIR / 'temp-audio.m4a'),
            remove_temp=True,
            threads=4
        )
        
        # Cleanup
        final_video.close()
        audio.close()
        
        print(f"✓ Video saved to {output_path}")
        return output_path