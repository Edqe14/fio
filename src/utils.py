from .consts import Format
from pathlib import Path
import hashlib
import os

def resolve_filename_from_disposition(content_disposition: str) -> str:
  filename = content_disposition.split('filename=')[1]
  filename = filename.replace('"', '')
  
  # Remove extension
  filename = filename.split('.')[0]

  return filename

def get_disposition(type: str = 'inline', filename: str|None = None, format: Format = 'webp'):
  if filename:
    return f'{type}; filename="{filename}.{format}"'

  return type

def get_cache_hash(attrs: dict) -> str:
  hash_object = hashlib.sha1()
  hash_object.update(str(frozenset(attrs.items())).encode('utf-8'))
  return hash_object.hexdigest()

def get_app_data_directory():
    if os.name == 'nt':  # Windows
        # Use LOCALAPPDATA instead of APPDATA
        return Path(os.getenv('LOCALAPPDATA'))  # Typically: C:\Users\<username>\AppData\Local
    else:  # macOS/Linux
        return Path.home() / ".local" / "share"  # Typically: ~/.local/share

def get_app_specific_directory(app_name):
    app_data_dir = get_app_data_directory()
    app_specific_dir = app_data_dir / app_name
    app_specific_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
    return app_specific_dir