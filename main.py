from agents.data_retriever import DataRetriever
from agents.style_planner import StylePlanner
from agents.image_director import ImageDirector
from agents.video_compositor import VideoCompositor
from models.data_models import VideoGenerationRequest
from config.settings import config
from pathlib import Path
import json

def generate_lyric_video(song_id: str, start_line: int = 1, 
                        end_line: int = None) -> Path:
    """
    Main orchestration function for generating lyric videos
    """
    print("=" * 60)
    print("🎵 LYRIC VIDEO GENERATOR")
    print("=" * 60)
    
    # Create necessary directories
    config.create_directories()
    
    # Create request
    request = VideoGenerationRequest(
        song_id=song_id,
        start_line=start_line,
        end_line=end_line
    )
    
    # Step 1: Data Retrieval
    print("\n📥 STEP 1: Fetching data from Supabase...")
    retriever = DataRetriever()
    song, all_lyrics, target_lyrics, audio_path = retriever.fetch_all_data(request)
    print(f"✓ Song: {song.title} by {song.artist}")
    print(f"✓ Generating lines {start_line} to {target_lyrics[-1].line_number}")
    print(f"✓ Total lines to generate: {len(target_lyrics)}")
    
    # Step 2: Style Planning
    print("\n🎨 STEP 2: Creating style guide...")
    planner = StylePlanner()
    style_guide = planner.create_style_guide(song, all_lyrics, target_lyrics)
    print(f"✓ Visual Style: {style_guide.visual_style}")
    print(f"✓ Story: {style_guide.segment_story}")
    
    # Step 3: Image Generation
    print("\n🖼️  STEP 3: Generating images...")
    director = ImageDirector()
    images = director.generate_all_images(target_lyrics, style_guide, song_id)
    print(f"✓ Generated {len(images)} images")
    
    # Step 4: Video Assembly
    print("\n🎬 STEP 4: Assembling video...")
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
        "style_guide": style_guide.dict(),
        "images": [img.dict() for img in images]
    }
    
    metadata_path = config.VIDEOS_DIR / f"{output_filename}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ VIDEO GENERATION COMPLETE!")
    print(f"📹 Video: {final_video}")
    print(f"📄 Metadata: {metadata_path}")
    print("=" * 60)
    
    return final_video

if __name__ == "__main__":
    # Example usage
    song_id = "7b9f8181-d21c-44e0-8790-b0639936b0a5"  # "Help Me!" song
    
    # Generate lines 1-10
    generate_lyric_video(
        song_id=song_id,
        start_line=1,
        end_line=12
    )