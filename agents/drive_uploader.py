"""
Simple Drive Uploader
Just uploads video file directly to Google Drive root folder
"""

from pathlib import Path
from typing import Dict
from utils.drive_client import DriveClient
from config.settings import config

class DriveUploader:
    def __init__(self):
        self.drive_client = DriveClient(
            credentials_path=str(config.GOOGLE_DRIVE_CREDENTIALS_PATH),
            root_folder_id=config.GOOGLE_DRIVE_ROOT_FOLDER_ID
        )
    
    def upload_video(self, 
                    video_path: Path,
                    song_id: str,
                    delete_after_upload: bool = True) -> Dict[str, str]:
        """
        Upload video directly to Drive root folder
        
        Args:
            video_path: Path to the video file
            song_id: Song ID (not used for folder creation anymore)
            delete_after_upload: Whether to delete local file after upload
            
        Returns:
            Dictionary with Drive file info
        """
        print("\n📤 UPLOADING TO GOOGLE DRIVE...")
        
        try:
            # Upload video directly to root folder (no subfolder)
            print(f"  → Uploading video: {video_path.name}...")
            video_result = self.drive_client.upload_file(
                file_path=video_path,
                folder_id=self.drive_client.root_folder_id,  # ← Upload to root!
                make_public=False
            )
            
            print(f"\n✅ Upload complete!")
            print(f"  🎬 Video: {video_result['web_view_link']}")
            
            # Delete local file if requested
            if delete_after_upload:
                print(f"\n🗑️  Deleting local file...")
                size_mb = video_path.stat().st_size / (1024 * 1024)
                video_path.unlink()
                print(f"  ✓ Deleted: {video_path.name} ({size_mb:.2f} MB freed)")
            
            return {
                'video_file_id': video_result['file_id'],
                'video_link': video_result['web_view_link'],
                'folder_id': self.drive_client.root_folder_id
            }
            
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            raise