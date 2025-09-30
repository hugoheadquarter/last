from utils.supabase_client import SupabaseClient
from models.data_models import SongMetadata, LyricLine, VideoGenerationRequest
from typing import List, Tuple
from pathlib import Path
from config.settings import config

class DataRetriever:
    def __init__(self):
        self.supabase = SupabaseClient()
    
    def fetch_all_data(self, request: VideoGenerationRequest) -> Tuple[SongMetadata, List[LyricLine], List[LyricLine], Path]:
        """
        Fetch all necessary data for video generation
        Returns: (song_metadata, all_lyrics, target_lyrics, audio_file_path)
        """
        # Fetch song metadata
        song = self.supabase.get_song_metadata(request.song_id)
        
        # Fetch all lyrics for context
        all_lyrics = self.supabase.get_all_lyrics_for_context(request.song_id)
        
        # Determine end_line if not specified
        end_line = request.end_line or max(l.line_number for l in all_lyrics)
        
        # Fetch target lyrics
        target_lyrics = self.supabase.get_lyrics(
            request.song_id,
            request.start_line,
            end_line
        )
        
        # Download audio file
        audio_filename = f"song_{request.song_id}.mp3"
        audio_path = config.TEMP_DIR / audio_filename
        
        if not audio_path.exists():
            self.supabase.download_audio_file(song.audio_file_path, audio_path)
        
        return song, all_lyrics, target_lyrics, audio_path