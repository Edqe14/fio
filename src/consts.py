from typing import Literal


image_types = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/tiff",
  "image/avif",
]

Format = Literal['webp', 'tiff', 'avif', 'png', 'jpeg']
FillMode = Literal['fill', 'contain', 'cover']

format_types: list[Format] = [
  'webp',
  'tiff',
  'avif',
  'png',
  'jpeg',
]

format_mime_types = {
  'webp': 'image/webp',
  'tiff': 'image/tiff',
  'avif': 'image/avif',
  'png': 'image/png',
  'jpeg': 'image/jpeg',
}