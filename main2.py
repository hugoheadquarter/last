"""
Batch Video Generator
Process all published Korean songs and generate videos for lines 1-8
"""

from main import generate_lyric_video
from utils.supabase_client import SupabaseClient
from config.settings import config
import time
from datetime import datetime

def get_all_published_korean_songs():
    """Fetch all published Korean songs from Supabase"""
    supabase = SupabaseClient()
    
    print("📥 Fetching all published Korean songs from database...")
    
    response = (
        supabase.client.table("songs")
        .select("id, title, language, is_published")
        .eq("is_published", True)
        .eq("language", "korean")
        .order("created_at", desc=True)  # Newest first
        .execute()
    )
    
    songs = response.data
    print(f"✓ Found {len(songs)} published Korean songs\n")
    
    return songs

def process_all_songs():
    """Process all songs and generate videos"""
    
    print("=" * 80)
    print("🎬 BATCH VIDEO GENERATOR - ALL KOREAN SONGS")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Fetch all songs
    songs = get_all_published_korean_songs()
    
    if len(songs) == 0:
        print("❌ No songs found!")
        return
    
    # Configuration
    START_LINE = 1
    END_LINE = 8
    UPLOAD_TO_DRIVE = True
    DELETE_AFTER_UPLOAD = True
    
    print("⚙️  CONFIGURATION:")
    print(f"  Lines: {START_LINE} to {END_LINE}")
    print(f"  Upload to Drive: {UPLOAD_TO_DRIVE}")
    print(f"  Delete after upload: {DELETE_AFTER_UPLOAD}")
    print()
    
    # Stats tracking
    successful = []
    failed = []
    skipped = []
    
    # Process each song
    for idx, song in enumerate(songs, 1):
        song_id = song['id']
        title = song['title']
        
        print("\n" + "=" * 80)
        print(f"📀 PROCESSING {idx}/{len(songs)}: {title}")
        print(f"   Song ID: {song_id}")
        print("=" * 80)
        
        try:
            # Check if video already exists in Drive (optional check)
            # You can add logic here to skip songs that are already processed
            
            # Generate video
            start_time = time.time()
            
            generate_lyric_video(
                song_id=song_id,
                start_line=START_LINE,
                end_line=END_LINE,
                upload_to_drive=UPLOAD_TO_DRIVE,
                delete_after_upload=DELETE_AFTER_UPLOAD
            )
            
            elapsed = time.time() - start_time
            
            successful.append({
                'song_id': song_id,
                'title': title,
                'time': elapsed
            })
            
            print(f"\n✅ SUCCESS! Completed in {elapsed:.1f}s")
            
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            failed.append({
                'song_id': song_id,
                'title': title,
                'error': str(e)
            })
            
            # Continue with next song even if this one fails
            print("   → Continuing with next song...")
        
        # Add a small delay between songs to avoid rate limits
        if idx < len(songs):
            print("\n⏳ Waiting 5 seconds before next song...")
            time.sleep(5)
    
    # Final Report
    print("\n\n" + "=" * 80)
    print("📊 BATCH PROCESSING COMPLETE!")
    print("=" * 80)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"✅ Successful: {len(successful)}/{len(songs)}")
    print(f"❌ Failed: {len(failed)}/{len(songs)}")
    print(f"⏭️  Skipped: {len(skipped)}/{len(songs)}")
    
    if successful:
        print("\n" + "-" * 80)
        print("✅ SUCCESSFUL SONGS:")
        print("-" * 80)
        for s in successful:
            print(f"  ✓ {s['title']} ({s['time']:.1f}s)")
    
    if failed:
        print("\n" + "-" * 80)
        print("❌ FAILED SONGS:")
        print("-" * 80)
        for f in failed:
            print(f"  ✗ {f['title']}")
            print(f"    Error: {f['error']}")
    
    # Save report to file
    report_path = config.VIDEOS_DIR / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("BATCH VIDEO GENERATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Songs: {len(songs)}\n")
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n")
        f.write(f"Skipped: {len(skipped)}\n\n")
        
        f.write("SUCCESSFUL:\n")
        for s in successful:
            f.write(f"  - {s['title']} (ID: {s['song_id']})\n")
        
        f.write("\nFAILED:\n")
        for fail in failed:
            f.write(f"  - {fail['title']} (ID: {fail['song_id']})\n")
            f.write(f"    Error: {fail['error']}\n")
    
    print(f"\n📄 Report saved: {report_path}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Confirm before starting
    print("\n⚠️  WARNING: This will process ALL published Korean songs!")
    print("   Each video will be uploaded to Drive and local copy deleted.")
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        process_all_songs()
    else:
        print("\n❌ Cancelled.")