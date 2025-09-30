from utils.claude_client import ClaudeClient
from models.data_models import LyricLine, StyleGuide
from typing import List
from pathlib import Path

class ReferenceSelector:
    def __init__(self):
        self.claude = ClaudeClient()
        
    def select_references(self, 
                        previous_prompts: List[str],
                        previous_paths: List[Path],
                        current_lyric: dict,
                        style_guide: StyleGuide,
                        line_number: int) -> dict:
        """
        Intelligently select 1-3 reference images that provide style consistency
        without causing compositional repetition
        """
        
        if len(previous_prompts) == 0:
            return {'paths': [], 'indices': [], 'reasoning': 'First image, no references'}
        
        # Format previous prompts for analysis
        prompts_analysis = "\n".join([
            f"Image {i}: {prompt[:150]}..."
            for i, prompt in enumerate(previous_prompts)
        ])
        
        # Ask Claude to select optimal references
        selection = self.claude.select_reference_images(
            prompts_analysis,
            current_lyric,
            style_guide.dict(),
            line_number,
            len(previous_prompts)
        )
        
        # Extract selected indices
        selected_indices = selection.get('selected_indices', [])
        reasoning = selection.get('reasoning', 'No reasoning provided')
        
        print(f"  → Reference selection: {selected_indices}")
        print(f"  → Reasoning: {reasoning[:100]}...")
        
        # Map indices to paths
        selected_paths = []
        for idx in selected_indices:
            if 0 <= idx < len(previous_paths):
                selected_paths.append(previous_paths[idx])
        
        return {
            'paths': selected_paths,
            'indices': selected_indices,
            'reasoning': reasoning
        }