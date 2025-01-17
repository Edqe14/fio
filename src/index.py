from io import BytesIO
from aiohttp import ClientSession
from fastapi import FastAPI, Response
from .cache.file import FileCache

from .utils import get_app_specific_directory, get_cache_hash, get_disposition, resolve_filename_from_disposition
from .consts import image_types, format_mime_types, Format, FillMode

# Add avif support
import pillow_avif
from PIL import Image

cache = FileCache(dir=get_app_specific_directory('fio'))
app = FastAPI()

@app.get('/')
def index():
  return {'message': 'Hello to FIO'}

@app.get('/o')
async def optimize(
  src: str,
  w: int|None = None,
  h: int|None = None,
  q: int = 80,
  format: Format = 'webp',
  mode: FillMode = 'contain'
):
  if q < 0 or q > 100:
    return {'message': 'Invalid quality value'}
  
  # Cache
  cache_hash = get_cache_hash({
    'src': src,
    'w': w,
    'h': h,
    'q': q,
    'format': format,
    'mode': mode,
  })
  
  cached = await cache.get(cache_hash)
  
  if cached:
    return Response(content=cached.data, media_type=format_mime_types[format], headers={
      'Content-Disposition': get_disposition(filename=cached.metadata['filename'], format=format),
    })
    
  # Not cached
  async with ClientSession() as session:
    async with session.get(src) as response:
      if response.status != 200:
        return {'message': 'Request failed'}

      content_disposition = response.headers.get('content-disposition')
      content_type = response.headers.get('content-type')
      
      # Validation
      if content_type is None:
        return {'message': 'Content type not found'}
      
      if content_type not in image_types:
        return {'message': 'Invalid image type'}
      
      # Read image
      img_data = await response.read()
      img = Image.open(BytesIO(img_data))
      
      # Transform
      if w is not None or h is not None:
        original_width, original_height = img.size

        if mode == 'contain':
          if w is not None and h is None:
            h = int((w / original_width) * original_height)
          elif h is not None and w is None:
            w = int((h / original_height) * original_width)
          elif w is not None and h is not None:
            aspect_ratio = original_width / original_height

            if w / h > aspect_ratio:
              w = int(h * aspect_ratio)
            else:
              h = int(w / aspect_ratio)
        elif mode == 'cover':
          if w is None or h is None:
            return {'message': 'Width and height must be provided for cover mode'}

          aspect_ratio = original_width / original_height
          target_aspect_ratio = w / h

          if target_aspect_ratio > aspect_ratio:
            new_height = int(original_width / target_aspect_ratio)
            top = (original_height - new_height) // 2
            img = img.crop((0, top, original_width, top + new_height))
          else:
            new_width = int(original_height * target_aspect_ratio)
            left = (original_width - new_width) // 2
            img = img.crop((left, 0, left + new_width, original_height))

        img = img.resize((w, h), resample=Image.Resampling.LANCZOS)

      # Output
      filename = None
      
      if content_disposition:
        filename = resolve_filename_from_disposition(content_disposition)
      
      output = BytesIO()
      img.save(output, format=format, quality=q)
      
      bytes_data = output.getvalue()
      
      await cache.set(cache_hash, bytes_data, metadata={
        'filename': filename,
        'w': w,
        'h': h,
        'q': q,
        'format': format,
        'mode': mode,
      })
        
      return Response(content=bytes_data, media_type=format_mime_types[format], headers={
        'Content-Disposition': get_disposition(filename=filename),
      })