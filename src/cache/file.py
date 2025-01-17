import json
from pathlib import Path

from .entry import CachedEntry
from .adapter import CacheAdapter

class FileCache(CacheAdapter):
  def __init__(self, dir: Path) -> None:
    super().__init__()
    self.directory = dir
    
  def get_path(self, key: str) -> Path:
    return self.directory / key
  
  def get_metadata_path(self, key: str) -> Path:
    return self.directory / f'{key}.json'
  
  async def get(self, key: str) -> None | CachedEntry:
    data = None
    metadata: dict | None = None

    try:
      with self.get_path(key).open('rb') as file:
        data = file.read()
    except FileNotFoundError:
      return None
    
    try:
      with self.get_metadata_path(key).open('r') as file:
        metadata_file = file.read()
        
      metadata = json.loads(metadata_file)
    except FileNotFoundError:
      return None
    
    return CachedEntry(data, metadata or {})
      

  async def set(self, key: str, data: bytes, metadata: dict) -> bool:
    try:
      with self.get_path(key).open('wb') as file:
        file.write(data)
        
      with self.get_metadata_path(key).open('w') as file:
        file.write(json.dumps(metadata))

      return True
    except Exception:
      # check if some data has been written
      if self.get_path(key).exists():
        self.get_path(key).unlink()
        
      if self.get_metadata_path(key).exists():
        self.get_metadata_path(key).unlink()
        
      return False
