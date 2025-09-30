import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file BEFORE accessing environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # API Keys
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    SEEDREAM_API_KEY = os.getenv("SEEDREAM_API_KEY")
    SEEDREAM_ENDPOINT = os.getenv("SEEDREAM_ENDPOINT")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / "output"
    FRAMES_DIR = OUTPUT_DIR / "frames"
    VIDEOS_DIR = OUTPUT_DIR / "videos"
    TEMP_DIR = OUTPUT_DIR / "temp"
    FONTS_DIR = BASE_DIR / "fonts"
    FONT_PATH = FONTS_DIR / "MaruBuri-Bold.ttf"
    
    # Video settings
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    IMAGE_SIZE = 1080
    FPS = 30
    
    # Layout settings
    IMAGE_TOP_PADDING = 150
    TEXT_START_Y = 1270  # 150 + 1080 + 40
    TEXT_SPACING = 78    # 30px between lines + 48px font size
    FONT_SIZE = 50
    TEXT_COLOR = (255, 255, 255)  # White
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.FRAMES_DIR.mkdir(parents=True, exist_ok=True)
        cls.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

config = Config()