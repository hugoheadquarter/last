"""
Test OAuth authentication with Google Drive
Run this to verify your setup works before integrating
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from utils.drive_client import DriveClient

def test_drive_oauth():
    """Test OAuth flow and Drive operations"""
    
    print("=" * 60)
    print("🔐 GOOGLE DRIVE OAUTH TEST")
    print("=" * 60)
    
    # Get credentials from .env
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    root_folder_id = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')
    
    if not credentials_path:
        print("❌ ERROR: GOOGLE_DRIVE_CREDENTIALS_PATH not set in .env")
        return False
    
    credentials_path = Path(credentials_path)
    if not credentials_path.exists():
        print(f"❌ ERROR: Credentials file not found: {credentials_path}")
        print(f"   Looking at: {credentials_path.absolute()}")
        return False
    
    print(f"\n✓ Credentials file: {credentials_path}")
    print(f"✓ Root folder ID: {root_folder_id or 'None (will upload to My Drive)'}")
    
    # Step 1: Authenticate
    print("\n" + "─" * 60)
    print("📋 Step 1: Authenticating with OAuth...")
    print("─" * 60)
    
    try:
        client = DriveClient(
            credentials_path=str(credentials_path),
            root_folder_id=root_folder_id
        )
        print("\n✅ Authentication successful!")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Create a test folder
    print("\n" + "─" * 60)
    print("📁 Step 2: Creating test folder...")
    print("─" * 60)
    
    try:
        test_folder_id = client.create_folder("Melos_OAuth_Test")
        print(f"✅ Test folder created/found: {test_folder_id}")
    except Exception as e:
        print(f"❌ Folder creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Create and upload a test file
    print("\n" + "─" * 60)
    print("📤 Step 3: Uploading test file...")
    print("─" * 60)
    
    try:
        # Create a small test file
        test_file = Path("/tmp/melos_test.txt")
        test_file.write_text("This is a test file from Melos Video Uploader!\nOAuth is working! 🎉")
        
        result = client.upload_file(
            file_path=test_file,
            folder_id=test_folder_id,
            make_public=False
        )
        
        print(f"\n✅ Upload successful!")
        print(f"  📄 File ID: {result['file_id']}")
        print(f"  🔗 View Link: {result['web_view_link']}")
        
        # Cleanup test file
        test_file.unlink()
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Get file info
    print("\n" + "─" * 60)
    print("ℹ️  Step 4: Verifying upload...")
    print("─" * 60)
    
    try:
        file_info = client.get_file_info(result['file_id'])
        print(f"✅ File verified in Drive:")
        print(f"  Name: {file_info['name']}")
        print(f"  Size: {file_info.get('size', 'N/A')} bytes")
        print(f"  Created: {file_info['createdTime']}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✓ OAuth authentication works")
    print("✓ Folder creation works")
    print("✓ File upload works")
    print("✓ File verification works")
    print("\n📁 Test folder in Drive: Melos_OAuth_Test")
    print("🔗 Check it out:", result['web_view_link'])
    print("\n✅ Ready to integrate with video generator!")
    
    return True

if __name__ == "__main__":
    success = test_drive_oauth()
    sys.exit(0 if success else 1)