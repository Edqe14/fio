class CachedEntry:
  def __init__(self, data: bytes, metadata: dict) -> None:
    self.data = data
    self.metadata = metadata