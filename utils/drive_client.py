"""
Google Drive Client using OAuth 2.0
Handles authentication, folder creation, and file uploads
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pathlib import Path
from typing import Optional, Dict
import os
import pickle

class DriveClient:
    # Scopes define what permissions we need
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_path: str, root_folder_id: Optional[str] = None):
        """
        Initialize Drive client with OAuth credentials
        
        Args:
            credentials_path: Path to OAuth client secret JSON
            root_folder_id: Optional root folder ID to organize uploads
        """
        self.credentials_path = Path(credentials_path)
        self.root_folder_id = root_folder_id
        self.token_path = self.credentials_path.parent / "token.pickle"
        self.service = None
        
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth authentication flow"""
        creds = None
        
        # Check if we have saved credentials
        if self.token_path.exists():
            print("  → Loading saved credentials...")
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("  → Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                print("  → Starting OAuth flow (browser will open)...")
                print("  → Please authorize the app in your browser")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                print("  ✓ Authorization successful!")
            
            # Save credentials for next time
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            print(f"  ✓ Credentials saved to {self.token_path}")
        
        # Build the Drive service
        self.service = build('drive', 'v3', credentials=creds)
        print("  ✓ Drive client ready!")
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Created folder ID
        """
        try:
            # Check if folder already exists
            parent_id = parent_folder_id or self.root_folder_id
            
            if parent_id:
                query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            else:
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"  → Folder '{folder_name}' already exists")
                return files[0]['id']
            
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"  ✓ Created folder: {folder_name} (ID: {folder_id})")
            
            return folder_id
            
        except HttpError as error:
            print(f"  ❌ Error creating folder: {error}")
            raise
    
    def upload_file(self, 
                   file_path: Path, 
                   folder_id: Optional[str] = None,
                   make_public: bool = False) -> Dict[str, str]:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Path to the file to upload
            folder_id: Optional folder ID to upload to
            make_public: Whether to make the file publicly accessible
            
        Returns:
            Dictionary with file_id, web_view_link, and download_link
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_name = file_path.name
            mime_type = self._get_mime_type(file_path)
            
            file_metadata = {'name': file_name}
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif self.root_folder_id:
                file_metadata['parents'] = [self.root_folder_id]
            
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )
            
            print(f"  → Uploading {file_name} ({file_path.stat().st_size / (1024*1024):.2f} MB)...")
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            
            print(f"  ✓ Upload complete! File ID: {file_id}")
            
            # Make public if requested
            if make_public:
                self._make_file_public(file_id)
                download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                download_link = file.get('webContentLink', web_view_link)
            
            return {
                'file_id': file_id,
                'web_view_link': web_view_link,
                'download_link': download_link,
                'folder_id': folder_id
            }
            
        except HttpError as error:
            print(f"  ❌ Upload error: {error}")
            raise
    
    def _make_file_public(self, file_id: str):
        """Make a file publicly accessible"""
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
            print(f"  ✓ File made public")
        except HttpError as error:
            print(f"  ⚠️  Could not make file public: {error}")
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type based on file extension"""
        extension = file_path.suffix.lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.mp3': 'audio/mpeg',
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def delete_file(self, file_id: str):
        """Delete a file from Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"  ✓ Deleted file: {file_id}")
        except HttpError as error:
            print(f"  ❌ Delete error: {error}")
            raise
    
    def get_file_info(self, file_id: str) -> Dict:
        """Get information about a file"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, webViewLink, createdTime'
            ).execute()
            return file
        except HttpError as error:
            print(f"  ❌ Error getting file info: {error}")
            raise