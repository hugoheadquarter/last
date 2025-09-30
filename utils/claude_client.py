from anthropic import Anthropic
from config.settings import config
import json
import re
from typing import List

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5"

    def generate_character_design(self, style_guide: dict, gender: str) -> str:
        """Generate a character design portrait for reference"""
        
        prompt = f"""Visual style: {style_guide['visual_style']}
Story context: {style_guide['segment_story']}

Create a CHARACTER DESIGN PORTRAIT for a {gender} character.

This is a REFERENCE IMAGE that will be used to maintain character consistency across multiple scenes.

REQUIREMENTS:
- Clean portrait of a young {gender} character
- Character should fill most of the frame
- Simple, neutral background (slightly blurred, minimal)
- Character facing forward or slightly angled (not profile, not back)
- Friendly, approachable expression
- Modern, casual clothing appropriate for the story
- Focus on CLEAR CHARACTER FEATURES: face, hair, body type, clothing style

STYLE:
- Follow the visual style described above
- Clean, simple composition
- No complex environments or props
- This is a character reference, not a scene

FORBIDDEN:
- NO text
- NO complex backgrounds

Image specs: 1080x1080 pixels

Respond with ONLY the Seedream prompt for this character design.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
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
2. What's the overall visual style? (art medium, colors, mood, aesthetic)
3. What's happening in this segment? (brief story summary)

IMPORTANT RULES:
- If this is a CONVERSATION (lyrics use "you/your", questions/responses between people):
  → Must feature TWO characters of OPPOSITE SEX (one male, one female)
- Characters should be placed in REAL ENVIRONMENTS (cafe, park, street, room)
- NO abstract colored backgrounds or gradient backgrounds
- NO split-screen compositions

Respond in JSON format:
{{
  "visual_style": "description of art style, colors, mood",
  "segment_story": "brief narrative including character genders if conversation",
  "is_conversation": true or false
}}
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)
    
    def generate_first_prompt(self, lyric_line: dict, style_guide: dict) -> str:
        """Generate prompt for the first image"""
        
        # Extract is_conversation from style_guide dict
        is_conversation = style_guide.get('is_conversation', True)
        
        # Build character rule based on conversation type
        if is_conversation:
            character_rule = "- This is a conversation, so show TWO characters of OPPOSITE SEX (one male, one female)"
        else:
            character_rule = "- Show the character(s) as described in the story"
        
        prompt = f"""Visual style: {style_guide['visual_style']}
Story context: {style_guide['segment_story']}

First lyric line: "{lyric_line['english_text']} / {lyric_line['korean_text']}"

Create an opening image focused on the CHARACTERS in a REAL ENVIRONMENT.

CHARACTER RULES:
{character_rule}
- Characters should fill significant frame space (not tiny in background)
- People are the primary focus, environment provides context

ENVIRONMENT RULES:
- Must be a REAL PLACE: cafe interior, park, street, room, etc.
- NO solid color backgrounds
- NO abstract gradient backgrounds
- NO colored geometric backgrounds
- Background should feel like an actual location

COMPOSITION RULES:
- NO split-screen compositions
- NO divider lines between characters
- Characters exist in the SAME unified space
- Single cohesive scene, not separated portraits

FORBIDDEN:
- NO text overlays

Image specs: 1080x1080 pixels (square format)

Respond with ONLY the Seedream prompt.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def generate_next_prompt(self, previous_prompts: List[str], 
                            current_lyric: dict, 
                            style_guide: dict,
                            line_number: int,
                            total_lines: int) -> dict:
        """Generate prompt for subsequent images with full visual history"""
        
        # Format all previous prompts
        prompts_history = "\n".join([
            f"Image {i+1}: {prompt[:120]}..."
            for i, prompt in enumerate(previous_prompts)
        ])
        
        # Extract is_conversation
        is_conversation = style_guide.get('is_conversation', True)
        
        # Build character rule
        if is_conversation:
            character_continuity = "- Conversation scenes require OPPOSITE SEX characters (male and female)"
        else:
            character_continuity = "- Maintain character consistency"
        
        prompt = f"""You're creating image #{line_number} of {total_lines} in a cinematic sequence.

STORY CONTEXT: {style_guide['segment_story']}

ALL PREVIOUS SCENE PROMPTS:
{prompts_history}

Current lyric: "{current_lyric['english_text']} / {current_lyric['korean_text']}"
Visual style: {style_guide['visual_style']}

UNDERSTANDING CHARACTER REFERENCES:
You will be provided with 2 character design portraits (male and female) as references.
These ensure consistent character appearance across all images.
The references show what the characters LOOK LIKE, not what scene to create.

YOUR JOB:
Create a NEW SCENE for this lyric using those same characters.

SCENE REQUIREMENTS:
- Place characters in a REAL ENVIRONMENT (cafe, park, street, room with details)
- Characters should fill significant frame space
- NO abstract/solid color backgrounds
- NO split-screen or divided compositions
- Characters in unified space

SCENE CONTINUITY:
{'- Keep both characters present (ongoing conversation)' if is_conversation else ''}
- If lyric says "you/your" → other person must be visible
- Scene can change naturally if lyric suggests it

CRITICAL: VISUAL VARIETY
Look at previous scenes. Make this one DISTINCTLY DIFFERENT:
- Different camera work
- Different character positions/interactions
- Different framing
- Different character gestures/face expressions
- Not just expression changes or slight variations
- BUT do not change their outfit.

FORBIDDEN:
- NO text

Respond in JSON:
{{
  "creative_reasoning": "How is this scene different from previous ones?",
  "seedream_prompt": "Describe the scene with characters from the reference portraits",
  "use_previous_as_reference": true
}}
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)
    
    def select_reference_images(self, 
                               prompts_analysis: str,
                               current_lyric: dict,
                               style_guide: dict,
                               line_number: int,
                               total_previous: int) -> dict:
        """Select optimal reference images to avoid compositional repetition"""
        
        prompt = f"""You're selecting reference images for AI image generation.

STORY CONTEXT: {style_guide['segment_story']}
CURRENT LYRIC (Line {line_number}): "{current_lyric['english_text']} / {current_lyric['korean_text']}"

PREVIOUS IMAGES:
{prompts_analysis}

CRITICAL UNDERSTANDING:
Reference images provide style (art style, colors, character designs) to Seedream, BUT Seedream often COPIES compositional elements too. This is a problem.

Example of what goes wrong:
- Reference has "man's back in foreground, woman in background"
- Seedream generates "man's back in foreground, woman in background" again
- Result: duplicate characters, boring repetition

YOUR TASK:
Select 1-3 references that provide style WITHOUT compositional problems.

AVOID SELECTING images with:
- "Over-shoulder" framing
- "From behind" angles
- "Person's back" in foreground
- "Foreground blur" with person
- "POV" shots
- Complex layered compositions
- "Split-screen" or "divided" compositions
- "Abstract background" or "colored background"

These cause Seedream to copy the framing, creating duplicates.

PREFER SELECTING images with:
- Simple, clean compositions
- Both characters clearly visible (no backs/foreground elements)
- Straightforward framing
- Real environments (cafe, park, etc.)

OTHER RULES:
- Character count must match (2 people scene → pick refs with 2 people)
- Pick compositionally diverse refs (don't pick 3 similar images)
- Prefer recent images (last 5) unless they're all similar
- If all recent are similar → pick only 1
- Fewer refs = safer (less compositional reinforcement)

Respond in JSON:
{{
  "selected_indices": [0, 1, 2],
  "reasoning": "Why these refs provide style without compositional problems"
}}

Indices are 0-based (0 = first image, {total_previous-1} = most recent)
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._extract_json(response.content[0].text)