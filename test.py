# test_complete_pipeline.py
"""
Complete test script for lyric video generator
Tests all components with detailed logging
"""

import os
import sys
from pathlib import Path
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def log(message, level="INFO"):
    """Pretty logging with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️ ",
        "TEST": "🧪"
    }
    symbol = symbols.get(level, "  ")
    print(f"[{timestamp}] {symbol} {message}")

def test_environment():
    """Test environment variables"""
    log("Testing environment variables...", "TEST")

    from config.settings import config
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY", 
        "ANTHROPIC_API_KEY",
        "SEEDREAM_API_KEY",
        "SEEDREAM_ENDPOINT"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            log(f"Missing: {var}", "ERROR")
        else:
            masked = value[:10] + "..." if len(value) > 10 else value
            log(f"Found: {var} = {masked}", "SUCCESS")
    
    if missing:
        log(f"Missing environment variables: {', '.join(missing)}", "ERROR")
        return False
    
    log("All environment variables present", "SUCCESS")
    return True

def test_dependencies():
    """Test required packages"""
    log("Testing Python dependencies...", "TEST")
    
    required_packages = {
        "supabase": "supabase",
        "anthropic": "anthropic",
        "requests": "requests",
        "moviepy.editor": "moviepy",
        "PIL": "pillow",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv",
        "tqdm": "tqdm",
        "korean_romanizer.romanizer": "korean-romanizer"
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            log(f"Found: {package_name}", "SUCCESS")
        except ImportError as e:
            missing.append(package_name)
            log(f"Missing: {package_name} - {str(e)}", "ERROR")
    
    if missing:
        log(f"Install missing packages: pip install {' '.join(missing)}", "ERROR")
        return False
    
    log("All dependencies installed", "SUCCESS")
    return True

def test_project_structure():
    """Test project directories and files"""
    log("Testing project structure...", "TEST")
    
    base_dir = Path(__file__).parent
    
    required_dirs = [
        "config",
        "agents", 
        "utils",
        "models",
        "output",
        "fonts"
    ]
    
    required_files = [
        "config/__init__.py",
        "config/settings.py",
        "agents/__init__.py",
        "agents/data_retriever.py",
        "agents/style_planner.py",
        "agents/image_director.py",
        "agents/video_compositor.py",
        "utils/__init__.py",
        "utils/supabase_client.py",
        "utils/claude_client.py",
        "utils/seedream_client.py",
        "utils/text_utils.py",
        "models/__init__.py",
        "models/data_models.py",
        "main.py",
        "fonts/MaruBuri-Bold.ttf"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            log(f"Directory exists: {dir_name}", "SUCCESS")
        else:
            log(f"Directory missing: {dir_name}", "ERROR")
            all_good = False
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            log(f"File exists: {file_name}", "SUCCESS")
        else:
            log(f"File missing: {file_name}", "ERROR")
            all_good = False
    
    return all_good

def test_imports():
    """Test importing project modules"""
    log("Testing project imports...", "TEST")
    
    try:
        from config.settings import config
        log(f"Config imported - Base dir: {config.BASE_DIR}", "SUCCESS")
        
        from utils.supabase_client import SupabaseClient
        log("SupabaseClient imported", "SUCCESS")
        
        from utils.claude_client import ClaudeClient
        log("ClaudeClient imported", "SUCCESS")
        
        from utils.seedream_client import SeedreamClient
        log("SeedreamClient imported", "SUCCESS")
        
        from utils.text_utils import korean_to_romanization
        log("Text utils imported", "SUCCESS")
        
        from models.data_models import VideoGenerationRequest
        log("Data models imported", "SUCCESS")
        
        from agents.data_retriever import DataRetriever
        log("DataRetriever imported", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"Import error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_supabase():
    """Test Supabase connection"""
    log("Testing Supabase connection...", "TEST")
    
    try:
        from utils.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        log("Supabase client created", "SUCCESS")
        
        # Test fetching a song
        test_song_id = "8e36b8ba-a752-4717-8f55-78f1d4996c8c"
        song = client.get_song_metadata(test_song_id)
        log(f"Fetched song: '{song.title}' by {song.artist}", "SUCCESS")
        log(f"  Duration: {song.duration_seconds}s", "INFO")
        log(f"  Audio path: {song.audio_file_path}", "INFO")
        
        # Test fetching lyrics
        lyrics = client.get_lyrics(test_song_id, start_line=1, end_line=3)
        log(f"Fetched {len(lyrics)} lyric lines", "SUCCESS")
        for lyric in lyrics:
            log(f"  Line {lyric.line_number}: {lyric.english_text[:30]}...", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Supabase error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_claude():
    """Test Claude API"""
    log("Testing Claude API...", "TEST")
    
    try:
        from utils.claude_client import ClaudeClient
        
        client = ClaudeClient()
        log("Claude client created", "SUCCESS")
        
        # Simple test call
        response = client.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Respond with exactly: 'API test successful'"
            }]
        )
        
        result = response.content[0].text
        log(f"Claude response: {result}", "SUCCESS")
        log(f"  Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Claude API error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_seedream():
    """Test Seedream API"""
    log("Testing Seedream API...", "TEST")
    
    try:
        from utils.seedream_client import SeedreamClient
        from config.settings import config
        
        client = SeedreamClient()
        log("Seedream client created", "SUCCESS")
        
        # Simple test generation
        log("Generating test image (this takes ~3-5 seconds)...", "INFO")
        result = client.generate_image(
            prompt="a simple red apple on a white table, minimal, clean",
            size="1080x1080"
        )
        
        if result.get('data') and len(result['data']) > 0:
            image_url = result['data'][0]['url']
            log(f"Image generated successfully", "SUCCESS")
            log(f"  URL: {image_url[:60]}...", "INFO")
            
            # Try to download it
            test_path = config.TEMP_DIR / "test_image.jpg"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            downloaded = client.download_image(image_url, test_path)
            log(f"Image downloaded to: {downloaded}", "SUCCESS")
            log(f"  File size: {downloaded.stat().st_size / 1024:.1f} KB", "INFO")
            
            return True
        else:
            log(f"Unexpected response format: {result}", "ERROR")
            return False
        
    except Exception as e:
        log(f"Seedream API error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_romanization():
    """Test Korean romanization"""
    log("Testing Korean romanization...", "TEST")
    
    try:
        from utils.text_utils import korean_to_romanization
        
        test_cases = [
            ("안녕하세요", "annyeonghaseyo"),
            ("도와주세요", "dowajuseyo"),
            ("감사합니다", "gamsahamnida")
        ]
        
        all_good = True
        for korean, expected in test_cases:
            result = korean_to_romanization(korean)
            if result.lower() == expected.lower():
                log(f"'{korean}' → '{result}' ✓", "SUCCESS")
            else:
                log(f"'{korean}' → '{result}' (expected: {expected})", "WARNING")
                all_good = False
        
        return all_good
        
    except Exception as e:
        log(f"Romanization error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_font():
    """Test font rendering"""
    log("Testing font rendering...", "TEST")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        from config.settings import config
        
        if not config.FONT_PATH.exists():
            log(f"Font file not found: {config.FONT_PATH}", "ERROR")
            return False
        
        log(f"Font file found: {config.FONT_PATH}", "SUCCESS")
        
        # Try to load font
        font = ImageFont.truetype(str(config.FONT_PATH), 48)
        log("Font loaded successfully", "SUCCESS")
        
        # Test rendering Korean text
        img = Image.new('RGB', (500, 100), color='black')
        draw = ImageDraw.Draw(img)
        test_text = "안녕하세요 Hello"
        draw.text((10, 10), test_text, font=font, fill='white')
        
        # Save test image
        test_path = config.TEMP_DIR / "test_font.png"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(test_path)
        log(f"Test image saved: {test_path}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"Font error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def test_minimal_pipeline():
    """Run a minimal end-to-end test with 1 line"""
    log("Testing minimal pipeline (1 line)...", "TEST")
    log("This will take ~30-60 seconds due to API calls", "INFO")
    
    try:
        from main import generate_lyric_video
        from config.settings import config
        
        # Generate just line 1
        test_song_id = "8e36b8ba-a752-4717-8f55-78f1d4996c8c"
        
        result = generate_lyric_video(
            song_id=test_song_id,
            start_line=1,
            end_line=1
        )
        
        if result.exists():
            file_size = result.stat().st_size / (1024 * 1024)  # MB
            log(f"Video created: {result}", "SUCCESS")
            log(f"  File size: {file_size:.2f} MB", "INFO")
            return True
        else:
            log("Video file not created", "ERROR")
            return False
        
    except Exception as e:
        log(f"Pipeline error: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("LYRIC VIDEO GENERATOR - COMPLETE SYSTEM TEST")
    print("="*80 + "\n")
    
    results = {}
    
    # Run tests
    tests = [
        ("Environment Variables", test_environment),
        ("Python Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Supabase Connection", test_supabase),
        ("Claude API", test_claude),
        ("Seedream API", test_seedream),
        ("Korean Romanization", test_romanization),
        ("Font Rendering", test_font),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'─'*80}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            log(f"Unexpected error in {test_name}: {str(e)}", "ERROR")
            results[test_name] = False
        print()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Decide if we should run minimal pipeline
    critical_tests = [
        "Environment Variables",
        "Python Dependencies", 
        "Module Imports",
        "Supabase Connection",
        "Claude API",
        "Seedream API"
    ]
    
    critical_passed = all(results.get(t, False) for t in critical_tests)
    
    if critical_passed:
        print("\n" + "="*80)
        print("All critical tests passed! Running minimal pipeline test...")
        print("="*80 + "\n")
        
        pipeline_result = test_minimal_pipeline()
        
        if pipeline_result:
            print("\n" + "="*80)
            print("🎉 ALL TESTS PASSED - SYSTEM READY!")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("⚠️  Pipeline test failed - check logs above")
            print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ Critical tests failed - fix issues before running pipeline")
        print("="*80)
        
        print("\nFailed critical tests:")
        for test in critical_tests:
            if not results.get(test, False):
                print(f"  - {test}")

if __name__ == "__main__":
    main()