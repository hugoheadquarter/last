"""
assemble_video.py
Simple script to assemble video from already-generated images
Usage: python assemble_video.py
"""

from agents.data_retriever import DataRetriever
from agents.video_compositor import VideoCompositor
from models.data_models import VideoGenerationRequest, GeneratedImage, LyricLine
from config.settings import config
from pathlib import Path
from typing import List
import json

def find_existing_images(song_id: str, start_line: int, end_line: int, 
                        lyrics: List[LyricLine]) -> List[GeneratedImage]:
    """Find already-generated images for the given line range"""
    frames_dir = config.FRAMES_DIR / song_id
    
    if not frames_dir.exists():
        raise FileNotFoundError(f"Frames directory not found: {frames_dir}")
    
    images = []
    missing_lines = []
    
    for lyric in lyrics:
        image_filename = f"line_{lyric.line_number:03d}.jpg"
        image_path = frames_dir / image_filename
        
        if not image_path.exists():
            missing_lines.append(lyric.line_number)
            continue
        
        images.append(GeneratedImage(
            line_number=lyric.line_number,
            image_path=str(image_path),
            prompt_used="N/A - using existing image",
            start_time=lyric.start_time_seconds,
            end_time=lyric.end_time_seconds,
            used_reference=True,
            reference_image=None
        ))
    
    if missing_lines:
        raise FileNotFoundError(
            f"Missing images for lines: {missing_lines}\n"
            f"Expected location: {frames_dir}\n"
            f"Generate these images first before assembling video."
        )
    
    return images

def assemble_from_existing_images(song_id: str, 
                                  start_line: int = 1, 
                                  end_line: int = None) -> Path:
    """
    Assemble video from already-generated images
    
    Args:
        song_id: Song ID from database
        start_line: Starting lyric line number
        end_line: Ending lyric line number (None = last line)
        
    Returns:
        Path to generated video file
    """
    print("=" * 60)
    print("🎬 VIDEO ASSEMBLY (FROM EXISTING IMAGES)")
    print("=" * 60)
    
    # Create necessary directories
    config.create_directories()
    
    # Create request
    request = VideoGenerationRequest(
        song_id=song_id,
        start_line=start_line,
        end_line=end_line
    )
    
    # Step 1: Fetch data (audio + lyrics only)
    print("\n📥 STEP 1: Fetching data from Supabase...")
    retriever = DataRetriever()
    song, all_lyrics, target_lyrics, audio_path = retriever.fetch_all_data(request)
    print(f"✓ Song: {song.title} by {song.artist}")
    print(f"✓ Lines {start_line} to {target_lyrics[-1].line_number}")
    print(f"✓ Total lines: {len(target_lyrics)}")
    
    # Step 2: Find existing images
    print("\n🖼️  STEP 2: Loading existing images...")
    images = find_existing_images(song_id, start_line, target_lyrics[-1].line_number, target_lyrics)
    print(f"✓ Found {len(images)} existing images")
    for img in images:
        print(f"  - Line {img.line_number}: {Path(img.image_path).name}")
    
    # Step 3: Assemble video
    print("\n🎬 STEP 3: Assembling video...")
    compositor = VideoCompositor()
    
    output_filename = f"song_{song_id}_lines_{start_line}-{target_lyrics[-1].line_number}.mp4"
    output_path = config.VIDEOS_DIR / output_filename
    
    final_video = compositor.assemble_video(images, target_lyrics, audio_path, output_path)
    
    # Save metadata
    metadata = {
        "song_id": song_id,
        "title": song.title,
        "artist": song.artist,
        "start_line": start_line,
        "end_line": target_lyrics[-1].line_number,
        "total_images": len(images),
        "assembled_from_existing": True,
        "images": [img.dict() for img in images]
    }
    
    metadata_path = config.VIDEOS_DIR / f"{output_filename}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ VIDEO ASSEMBLY COMPLETE!")
    print(f"📹 Video: {final_video}")
    print(f"📄 Metadata: {metadata_path}")
    print("=" * 60)
    
    return final_video

if __name__ == "__main__":
    # Edit these values:
    SONG_ID = "7b9f8181-d21c-44e0-8790-b0639936b0a5"  # Your song ID
    START_LINE = 1
    END_LINE = 10  # Or None for all lines
    
    try:
        assemble_from_existing_images(
            song_id=SONG_ID,
            start_line=START_LINE,
            end_line=END_LINE
        )
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure images exist at:")
        print(f"  {config.FRAMES_DIR / SONG_ID}/")
        print("\nExpected files:")
        for i in range(START_LINE, (END_LINE or START_LINE) + 1):
            print(f"  - line_{i:03d}.jpg")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()