from supabase import create_client, Client
from config.settings import config
from models.data_models import SongMetadata, LyricLine
from typing import List, Optional
import requests
import json
from pathlib import Path

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_KEY
        )
    
    def get_song_metadata(self, song_id: str) -> SongMetadata:
        """Fetch song metadata from database"""
        response = (
            self.client.table("songs")
            .select("*")
            .eq("id", song_id)
            .single()
            .execute()
        )
        return SongMetadata(**response.data)
    
    def get_lyrics(self, song_id: str, start_line: int = 1, 
                   end_line: Optional[int] = None) -> List[LyricLine]:
        """Fetch lyrics for a song, optionally filtered by line range"""
        query = (
            self.client.table("lyrics")
            .select("*")
            .eq("song_id", song_id)
            .order("line_number")
        )
        
        if end_line:
            query = query.gte("line_number", start_line).lte("line_number", end_line)
        else:
            query = query.gte("line_number", start_line)
        
        response = query.execute()
        
        # Parse breakdown_data from JSON string to dict
        lyrics = []
        for line in response.data:
            if line.get('breakdown_data') and isinstance(line['breakdown_data'], str):
                line['breakdown_data'] = json.loads(line['breakdown_data'])
            lyrics.append(LyricLine(**line))
        
        return lyrics
    
    def get_all_lyrics_for_context(self, song_id: str) -> List[LyricLine]:
        """Fetch ALL lyrics for context understanding"""
        response = (
            self.client.table("lyrics")
            .select("*")
            .eq("song_id", song_id)
            .order("line_number")
            .execute()
        )
        
        # Parse breakdown_data from JSON string to dict
        lyrics = []
        for line in response.data:
            if line.get('breakdown_data') and isinstance(line['breakdown_data'], str):
                line['breakdown_data'] = json.loads(line['breakdown_data'])
            lyrics.append(LyricLine(**line))
        
        return lyrics
        
    def download_audio_file(self, audio_path: str, output_path: Path) -> Path:
        """Download audio file from Supabase storage"""
        base_url = config.SUPABASE_URL.rstrip('/rest/v1')
        
        # Try multiple URL patterns (the stored path might be the full path in the audio bucket)
        possible_urls = [
            f"{base_url}/storage/v1/object/public/audio/{audio_path}",
            f"{base_url}/storage/v1/object/public/{audio_path}",
            f"{base_url}/storage/v1/object/public/audio/{audio_path.replace('albums/', '')}",
        ]
        
        successful_download = False
        
        for url in possible_urls:
            try:
                print(f"  Trying: {url[:80]}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Success! Save the file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)
                print(f"  ✓ Downloaded from: {url[:80]}...")
                successful_download = True
                break
                
            except requests.exceptions.HTTPError as e:
                print(f"  ✗ Failed with status {e.response.status_code}")
                continue
            except Exception as e:
                print(f"  ✗ Failed: {str(e)}")
                continue
        
        if not successful_download:
            raise Exception(f"Could not download audio from any URL pattern. Path: {audio_path}")
        
        return output_path