from agents.data_retriever import DataRetriever
from agents.style_planner import StylePlanner
from agents.image_director import ImageDirector
from agents.video_compositor import VideoCompositor
from agents.drive_uploader import DriveUploader
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
                        is_conversation: Optional[bool] = None,
                        upload_to_drive: bool = False,
                        delete_after_upload: bool = True) -> Path:
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
        upload_to_drive: Whether to upload video to Google Drive
        delete_after_upload: Whether to delete local video after upload (only if upload_to_drive=True)
        
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
        
        # Upload to Drive and delete local copy
        generate_lyric_video(
            "song-id", 1, 10,
            upload_to_drive=True,
            delete_after_upload=True
        )
        
        # Upload to Drive but keep local copy
        generate_lyric_video(
            "song-id", 1, 10,
            upload_to_drive=True,
            delete_after_upload=False
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
    
    # Step 5: Upload to Google Drive (optional)
    if upload_to_drive:
        print("\n📤 STEP 5: Uploading to Google Drive...")
        try:
            uploader = DriveUploader()
            drive_result = uploader.upload_video(
                video_path=final_video,
                song_id=song_id,
                delete_after_upload=delete_after_upload
            )
            print("\n" + "=" * 60)
            print("✅ UPLOAD COMPLETE!")
            print(f"🔗 View on Drive: {drive_result['video_link']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n⚠️  Upload failed: {e}")
            print(f"📹 Video saved locally: {final_video}")
    
    return final_video

if __name__ == "__main__":
    generate_lyric_video(
        song_id="54278559-b036-446a-ab2a-30f8ea069729",
        start_line=1,
        end_line=16,
        #custom_story="Digital illustration of a fierce pink cartoon teddy bear with a hyperpop street attitude walking through a lively Seoul city crosswalk, wearing edgy fashion like a black sleeveless top with a cracked heart emblem, a spiked choker, a pleated mini skirt with a chain, fishnet stockings, chunky platform boots, the bear’s determined expression showing bold confidence while surrounded by colorful Korean storefront signs, bright daylight reflections, and dynamic crowds, vibrant urban hues with saturated yellows, blues, and pinks, strong bold outlines and lively cartoon detailing, square composition with the bear dominating the center as it strides forward with attitude, capturing the playful chaos of pop culture and punk energy in a Seoul city vibe. IMPORTANT: The bear is the main character in the story. Also You dont have to make two human charactesr appear in every scene - just make one of them appear when you think it's natural. put focus on the bear. Also do not make the body of a bear look like human. The teddy bear body stays as a teddy bear, regardless of what clothe she wears.",
        upload_to_drive=False,
    )

    
#5f406392-77a2-43e3-b928-cf8ef62a291a