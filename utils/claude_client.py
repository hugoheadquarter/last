from anthropic import Anthropic
from config.settings import config
import json
import re

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5"
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Claude's response, handling markdown code blocks"""
        # Try to parse as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If all else fails, raise error with the actual response
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

Create a visual foundation for this segment:
1. What's the overall visual style? (art medium, colors, mood, aesthetic)
2. What's happening in this segment of the song? (brief story summary)

Respond in JSON format:
{{
  "visual_style": "description of art style, colors, mood",
  "segment_story": "brief narrative of what's happening"
}}

Keep it simple - just style and vibe. No rigid rules about characters or settings.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)
    
    def generate_first_prompt(self, lyric_line: dict, style_guide: dict) -> str:
        """Generate prompt for the first image"""
        prompt = f"""Visual style: {style_guide['visual_style']}
Story context: {style_guide['segment_story']}

First lyric line: "{lyric_line['english_text']} / {lyric_line['korean_text']}"

Create an opening image that captures the emotion and action of this line.
Image specs: 1080x1080 pixels (square format, 1:1).

CRITICAL RULES:
- NO speech bubbles
- NO text overlays
- NO Korean or English words in the image
- START your prompt with a specific camera angle (wide shot, close-up, etc.)
- Focus on visual storytelling through character expression and body language

Respond with ONLY the Seedream prompt text, starting with the camera angle.
Example format: "Wide establishing shot, confused young traveler standing..."
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def generate_next_prompt(self, previous_prompt: str, 
                            current_lyric: dict, 
                            style_guide: dict) -> dict:
        """Generate prompt for subsequent images with creative reasoning"""
        prompt = f"""You're creating image #{current_lyric.get('line_number', 'N')} in a cinematic sequence.

Previous prompt (STYLE REFERENCE ONLY): "{previous_prompt}"
Current lyric: "{current_lyric['english_text']} / {current_lyric['korean_text']}"
Base visual style: {style_guide['visual_style']}

YOUR MISSION: Create a visually DISTINCT shot that maintains style but varies composition dramatically.

WHAT TO KEEP FROM REFERENCE:
✓ Art style (flat illustration, bold outlines, etc.)
✓ Color palette (yellows, blues, coral, etc.)
✓ Character design consistency

WHAT MUST CHANGE:
✗ Camera angle (NEVER repeat the same angle)
✗ Character pose and gesture
✗ Composition and framing
✗ Location (if lyric suggests scene change)

ABSOLUTE RULES:
🚫 NO speech bubbles
🚫 NO text in image
🚫 NO Korean/English words visible
🚫 NO same pose as previous

CAMERA VARIETY OPTIONS:
- Close-up (face, hands, detail shot)
- Wide/establishing shot
- Over-shoulder view
- Bird's eye / top-down view
- Low angle looking up
- Profile / side view
- From behind / back view
- Dutch angle / tilted
- POV shot
- Medium shot (waist up)

CREATIVE CHECKLIST:
☐ Is this angle different from "{previous_prompt[:50]}..."?
☐ Does the character pose convey the lyric's emotion?
☐ Is there visual variety in zoom/perspective?
☐ Does the scene progress naturally?

If unsure, choose: close-up, profile, or from-behind views.

Respond in JSON:
{{
  "creative_reasoning": "Why this specific angle/pose works for this lyric and how it differs from previous",
  "seedream_prompt": "START with camera angle, then scene description. NO text/bubbles. Format: 'Close-up profile shot, young traveler...'",
  "use_previous_as_reference": true
}}
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)