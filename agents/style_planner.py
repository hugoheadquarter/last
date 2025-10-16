from utils.claude_client import ClaudeClient
from models.data_models import SongMetadata, LyricLine, StyleGuide, CustomCreativeInput
from typing import List, Optional

class StylePlanner:
    def __init__(self):
        self.claude = ClaudeClient()
    
    def create_style_guide(self, song: SongMetadata, 
                          all_lyrics: List[LyricLine],
                          target_lyrics: List[LyricLine],
                          custom_input: Optional[CustomCreativeInput] = None) -> StyleGuide:
        """Generate style guide for the video segment, using custom input if provided"""
        
        # If custom input provided, use it directly
        if custom_input and custom_input.story_description:
            print("  ℹ️  Using custom story description")
            print(f"     Story: {custom_input.story_description[:100]}...")
            
            return StyleGuide(
                visual_style="High-quality Korean webtoon style with clean digital illustration, soft natural colors, expressive faces, modern fashion, atmospheric lighting",
                segment_story=custom_input.story_description,
                is_conversation=custom_input.is_conversation if custom_input.is_conversation is not None else True
            )
        
        # Otherwise, auto-generate as before
        print("  ℹ️  Auto-generating story from lyrics")
        
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