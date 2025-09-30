from pathlib import Path
from datetime import datetime
from typing import List

class GenerationLogger:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear file if exists
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LYRIC VIDEO GENERATION LOG\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, content: str):
        """Append content to log file"""
        with open(self.output_path, 'a', encoding='utf-8') as f:
            f.write(content + "\n")
    
    def log_section(self, title: str):
        """Log a section header"""
        self.log("\n" + "=" * 80)
        self.log(title)
        self.log("=" * 80 + "\n")
    
    def log_subsection(self, title: str):
        """Log a subsection header"""
        self.log("\n" + "-" * 80)
        self.log(title)
        self.log("-" * 80 + "\n")
    
    def log_style_guide(self, style_guide: dict):
        """Log the style guide"""
        self.log_section("STYLE GUIDE GENERATION")
        self.log(f"Visual Style:\n{style_guide['visual_style']}\n")
        self.log(f"Story Context:\n{style_guide['segment_story']}\n")
    
    def log_line_start(self, line_number: int, english: str, korean: str):
        """Log the start of a new line generation"""
        self.log_section(f"LINE {line_number}: {english}")
        self.log(f"Korean: {korean}\n")
    
    def log_prompt_generation(self, prompt: str, reasoning: str = None):
        """Log the generated prompt"""
        self.log_subsection("CLAUDE PROMPT GENERATION")
        if reasoning:
            self.log(f"Creative Reasoning:\n{reasoning}\n")
        self.log(f"Seedream Prompt:\n{prompt}\n")
    
    def log_reference_selection(self, selected_indices: List[int], reasoning: str, total_available: int):
        """Log reference selection decision"""
        self.log_subsection("REFERENCE SELECTION")
        self.log(f"Available images: 0-{total_available-1}")
        self.log(f"Selected indices: {selected_indices}")
        self.log(f"Reasoning:\n{reasoning}\n")
    
    def log_generation_result(self, success: bool, generation_time: float, image_path: str):
        """Log the generation result"""
        self.log_subsection("GENERATION RESULT")
        self.log(f"Status: {'SUCCESS' if success else 'FAILED'}")
        self.log(f"Generation Time: {generation_time:.2f}s")
        self.log(f"Image Path: {image_path}\n")
    
    def log_summary(self, total_images: int, total_time: float):
        """Log final summary"""
        self.log_section("GENERATION SUMMARY")
        self.log(f"Total Images Generated: {total_images}")
        self.log(f"Total Time: {total_time:.2f}s")
        self.log(f"Average Time per Image: {total_time/total_images:.2f}s\n")