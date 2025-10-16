from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LyricLine(BaseModel):
    id: str
    song_id: str
    line_number: int
    english_text: str
    korean_text: str
    start_time_seconds: float
    end_time_seconds: float
    voice_over_file_path: Optional[str]
    breakdown_data: Optional[dict]
    is_published: bool

class SongMetadata(BaseModel):
    id: str
    title: str
    artist: Optional[str] = None
    description: Optional[str]
    audio_file_path: str
    duration_seconds: Optional[float] = None
    artist_gender: Optional[str]
    original_lyrics_text: Optional[str]
    cover_image_prompt: Optional[str]

class CustomCreativeInput(BaseModel):
    """Optional custom input to override auto-generation"""
    story_description: Optional[str] = None  # Custom story narrative
    character_male_description: Optional[str] = None  # Custom male character
    character_female_description: Optional[str] = None  # Custom female character
    is_conversation: Optional[bool] = None  # Override conversation detection

class StyleGuide(BaseModel):
    visual_style: str
    segment_story: str
    is_conversation: bool = True 

class ImagePromptDecision(BaseModel):
    line_number: int
    creative_reasoning: str
    seedream_prompt: str
    use_previous_as_reference: bool

class GeneratedImage(BaseModel):
    line_number: int
    image_path: str
    prompt_used: str
    start_time: float
    end_time: float
    used_reference: bool
    reference_image: Optional[str] = None
    generation_time: Optional[float] = None

class VideoGenerationRequest(BaseModel):
    song_id: str
    start_line: int = 1
    end_line: Optional[int] = None
    resolution: str = "4k"
    output_filename: Optional[str] = None
    custom_input: Optional[CustomCreativeInput] = None