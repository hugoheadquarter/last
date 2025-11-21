from anthropic import Anthropic
from config.settings import config
import json
import re
from typing import List

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5"
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Claude's response, handling markdown code blocks"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not extract JSON from response: {text[:200]}")
    
    def create_style_guide(self, song_metadata: dict, 
                          all_lyrics: str, target_lyrics: str) -> dict:
        """Generate initial style guide and story concept"""
        prompt = f"""You're creating a lyric video for a Korean learning song.

Full song context:
{all_lyrics}

Target segment we're generating:
{target_lyrics}

Song description: {song_metadata.get('description', 'N/A')}

Analyze the lyrics:
1. Is this a conversation between two people, or a solo narrative?
2. What's happening in this segment? (brief story summary)

FIXED VISUAL STYLE:
You must use high-quality Korean webtoon art style with these characteristics:
- Clean digital illustration with smooth linework
- Soft, natural color palette (pastels, warm tones, muted colors)
- Expressive faces with detailed eyes
- Modern, trendy fashion
- Atmospheric lighting and subtle gradients
- Professional webtoon quality (think Lezhin, Naver Webtoon premium series)

IMPORTANT RULES:
- If this is a CONVERSATION (lyrics use "you/your", questions/responses between people):
  → Must feature TWO characters of OPPOSITE SEX (one male, one female)
- Characters should be placed in WEBTOON ENVIRONMENTS (cafe, park, street, room)
- NO abstract colored backgrounds or gradient backgrounds
- NO split-screen compositions

Respond in JSON format:
{{
  "visual_style": "High-quality Korean webtoon style with clean digital illustration, soft natural colors, expressive faces, modern fashion, atmospheric lighting",
  "segment_story": "brief narrative including character genders if conversation",
  "is_conversation": true or false
}}

Note: visual_style field should always contain the exact text above for consistency.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)
    
    def generate_character_design(self, style_guide: dict, gender: str) -> str:
        """Generate a character design portrait for reference"""
        
        prompt = f"""High-quality Korean webtoon style
    - No background
    - The face should appear natural, without glittering or sparkling effects.
    - Professional webtoon quality 

    Story context: {style_guide['segment_story']}

    Create a CHARACTER DESIGN PORTRAIT for a {gender} character in this webtoon style.

    This is a REFERENCE IMAGE for character consistency across scenes.

    REQUIREMENTS:
    - Young {gender} character (early 20s)
    - Character fills most of frame (shoulders and head visible)
    - Character facing forward or slightly angled (3/4 view)
    - Friendly, approachable expression
    - Clear features: face, hair, clothing details
    - Webtoon-quality rendering: smooth shading, clean lines, professional finish

    FORBIDDEN:
    - NO text

    Image specs: 1080x1080 pixels

    Respond with ONLY the Seedream prompt for this {gender} character in high-quality webtoon style.
    """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def generate_first_prompt(self, lyric_line: dict, style_guide: dict, 
                             character_design_prompts: List[str]) -> str:
        """Generate prompt for the first image"""
        
        is_conversation = style_guide.get('is_conversation', True)
        
        if is_conversation:
            character_rule = "- Show TWO characters (male and female from the reference portraits)"
        else:
            character_rule = "- Show the character from the reference portrait"
        
        prompt = f"""Visual style: {style_guide['visual_style']}
Story context: {style_guide['segment_story']}

First lyric line: "{lyric_line['english_text']} / {lyric_line['korean_text']}"

CHARACTER REFERENCE INFORMATION:
You will receive reference portrait images. Here are the exact prompts used to create them:

Male character prompt:
{character_design_prompts[0]}

Female character prompt:
{character_design_prompts[1]}

These references show what the characters LOOK LIKE (facial features, hair, outfits, style).
Your job is to create a SCENE using these exact same characters.

Create an opening scene focused on the CHARACTERS in a WEBTOON ENVIRONMENT.

CHARACTER RULES:
{character_rule}
- Characters should look EXACTLY as described in the reference prompts above
- SAME outfits, SAME hairstyles, SAME features
- Characters should fill significant frame space
- People are the primary focus

ENVIRONMENT RULES:
- Must be a WEBTOON PLACE: cafe interior, park, street, room, etc with details
- NO solid color backgrounds
- NO abstract gradient backgrounds
- Background should feel like an actual location

COMPOSITION RULES:
- NO split-screen compositions
- NO divider lines between characters
- Characters in the SAME unified space
- Single cohesive scene

FORBIDDEN:
- NO text overlays
- DO NOT change character appearance from references

Image specs: 1080x1080 pixels (square format)

Respond with ONLY the Seedream prompt.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def generate_next_prompt(self, previous_prompts: List[str], 
                            current_lyric: dict, 
                            style_guide: dict,
                            character_design_prompts: List[str],
                            line_number: int,
                            total_lines: int) -> dict:
        """Generate prompt for subsequent images"""
        
        prompts_history = "\n".join([
            f"Image {i+1}: {prompt[:120]}..."
            for i, prompt in enumerate(previous_prompts)
        ])
        
        is_conversation = style_guide.get('is_conversation', True)
        
        prompt = f"""You're creating image #{line_number} of {total_lines} in a cinematic sequence.

STORY CONTEXT: {style_guide['segment_story']}

ALL PREVIOUS SCENE PROMPTS:
{prompts_history}

Current lyric: "{current_lyric['english_text']} / {current_lyric['korean_text']}"
Visual style: {style_guide['visual_style']}

CHARACTER REFERENCE INFORMATION:
You will receive reference portrait images. Here are the exact prompts used to create them:

Male character prompt:
{character_design_prompts[0]}

Female character prompt:
{character_design_prompts[1]}

These references show what the characters LOOK LIKE (facial features, hair, outfits, style).
Use these EXACT character descriptions in your scene.

YOUR JOB:
Create a NEW SCENE for this lyric using those same characters with their exact appearance.

SCENE REQUIREMENTS:
- Place characters in a WEBTOON ENVIRONMENT (cafe, park, street, room with details)
- Characters should look EXACTLY as described in the reference prompts
- SAME outfits, SAME hairstyles, SAME features
- Characters should fill significant frame space
- NO abstract/solid color backgrounds
- NO split-screen or divided compositions
- NO divider lines between characters
- Characters in unified space

SCENE CONTINUITY:
{'- Keep both characters present (ongoing conversation)' if is_conversation else ''}
- If lyric says "you/your" → other person must be visible
- Scene can change naturally if lyric suggests it

CRITICAL: VISUAL VARIETY
Look at previous scenes. Make this one DISTINCTLY DIFFERENT:
- Different camera work
- Different character positions/interactions
- Different character gestures/face expressions
- Different framing
- NOT just expression changes or slight variations

Think about how the scene composition, character arrangement, and perspective can tell the story differently.

FORBIDDEN:
- NO text
- DO NOT change character appearance (outfits, hair, features)

IMPORTANT: Characters should not look at the viewer. Instead, they must direct their gaze toward each other, toward objects in the environment, toward what they are gesturing at, etc.

Respond in JSON:
{{
  "creative_reasoning": "How is this scene different from previous ones?",
  "seedream_prompt": "Describe the scene with characters matching the exact reference descriptions",
  "use_previous_as_reference": true
}}
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)