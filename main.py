from agents.data_retriever import DataRetriever
from agents.style_planner import StylePlanner
from agents.image_director import ImageDirector
from agents.video_compositor import VideoCompositor
from models.data_models import VideoGenerationRequest, CustomCreativeInput
from config.settings import config
from pathlib import Path
from typing import Optional
import json

def generate_lyric_video(song_id: str, 
                        start_line: int = 1, 
                        end_line: Optional[int] = None,
                        custom_story: Optional[str] = None,
                        custom_male_character: Optional[str] = None,
                        custom_female_character: Optional[str] = None,
                        is_conversation: Optional[bool] = None) -> Path:
    """
    Main orchestration function for generating lyric videos
    
    Args:
        song_id: Song ID from database
        start_line: Starting lyric line number
        end_line: Ending lyric line number (None = last line)
        custom_story: Optional custom story description to override auto-generation
        custom_male_character: Optional custom male character description
        custom_female_character: Optional custom female character description
        is_conversation: Optional override for conversation detection
        
    Returns:
        Path to generated video file
        
    Examples:
        # Fully automatic
        generate_lyric_video("song-id", 1, 10)
        
        # Custom story only
        generate_lyric_video(
            "song-id", 1, 10,
            custom_story="Two friends meeting at a cafe"
        )
        
        # Full custom control
        generate_lyric_video(
            "song-id", 1, 10,
            custom_story="College students studying together",
            custom_male_character="Young man, glasses, navy hoodie",
            custom_female_character="Young woman, ponytail, cream cardigan",
            is_conversation=True
        )
    """
    print("=" * 60)
    print("🎵 LYRIC VIDEO GENERATOR")
    print("=" * 60)
    
    # Create necessary directories
    config.create_directories()
    
    # Build custom input if any provided
    custom_input = None
    if any([custom_story, custom_male_character, custom_female_character, is_conversation is not None]):
        custom_input = CustomCreativeInput(
            story_description=custom_story,
            character_male_description=custom_male_character,
            character_female_description=custom_female_character,
            is_conversation=is_conversation
        )
        print("\n🎨 CUSTOM INPUT PROVIDED:")
        if custom_story:
            print(f"  📖 Story: {custom_story[:80]}...")
        if custom_male_character:
            print(f"  👨 Male Character: {custom_male_character[:80]}...")
        if custom_female_character:
            print(f"  👩 Female Character: {custom_female_character[:80]}...")
        if is_conversation is not None:
            print(f"  💬 Is Conversation: {is_conversation}")
    
    # Create request
    request = VideoGenerationRequest(
        song_id=song_id,
        start_line=start_line,
        end_line=end_line,
        custom_input=custom_input
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
    style_guide = planner.create_style_guide(song, all_lyrics, target_lyrics, custom_input)
    print(f"✓ Visual Style: {style_guide.visual_style[:80]}...")
    print(f"✓ Story: {style_guide.segment_story[:80]}...")
    print(f"✓ Is Conversation: {style_guide.is_conversation}")
    
    # Step 3: Image Generation
    print("\n🖼️  STEP 3: Generating images...")
    director = ImageDirector()
    images = director.generate_all_images(target_lyrics, style_guide, song_id, custom_input)
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
        "custom_input": custom_input.dict() if custom_input else None,
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
    generate_lyric_video(
        song_id="2cabb33e-00e7-4033-b113-719ac733cb98",
        start_line=1,
        end_line=7,
        is_conversation=False
    )
    
    # Example 2: Custom story only
    # generate_lyric_video(
    #     song_id="8e36b8ba-a752-4717-8f55-78f1d4996c8c",
    #     start_line=1,
    #     end_line=3,
    #     custom_story="A lost tourist asking a friendly local for directions in Seoul, with the local patiently helping despite the language barrier"
    # )
    
    # Example 3: Full custom control
    # generate_lyric_video(
    #     song_id="8e36b8ba-a752-4717-8f55-78f1d4996c8c",
    #     start_line=1,
    #     end_line=3,
    #     custom_story="Two college students studying Korean together in a university library, with one asking for help and the other explaining patiently",
    #     custom_male_character="Young Korean man in early 20s, short neat black hair, round wire-frame glasses, wearing a gray university hoodie with a book logo, friendly and patient expression, holding a textbook, Korean webtoon style, soft colors, clean illustration",
    #     custom_female_character="Young woman in early 20s, long brown hair in a ponytail, wearing a cream-colored cardigan over a white t-shirt and light blue jeans, confused but eager expression, holding a notebook, Korean webtoon style, soft colors, clean illustration",
    #     is_conversation=True
    # )