from utils.claude_client import ClaudeClient
from models.data_models import SongMetadata, LyricLine, StyleGuide
from typing import List

class StylePlanner:
    def __init__(self):
        self.claude = ClaudeClient()
    
    def create_style_guide(self, song: SongMetadata, 
                          all_lyrics: List[LyricLine],
                          target_lyrics: List[LyricLine]) -> StyleGuide:
        """Generate style guide for the video segment"""
        
        # Format lyrics as text
        all_lyrics_text = "\n".join([
            f"Line {l.line_number}: {l.english_text} / {l.korean_text}"
            for l in all_lyrics
        ])
        
        target_lyrics_text = "\n".join([
            f"Line {l.line_number}: {l.english_text} / {l.korean_text}"
            for l in target_lyrics
        ])
        
        song_dict = {
            'description': song.description,
            'title': song.title,
            'artist': song.artist
        }
        
        style_data = self.claude.create_style_guide(
            song_dict,
            all_lyrics_text,
            target_lyrics_text
        )
        
        return StyleGuide(**style_data)