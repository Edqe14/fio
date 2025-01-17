from .entry import CachedEntry

class CacheAdapter:
  async def get(self, key: str) -> CachedEntry | None:
    return None

  async def set(self, hash: str, data: bytes, metadata: dict) -> bool:
    return False