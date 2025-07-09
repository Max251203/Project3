from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime


def get_datetime_from_image(filepath: str) -> datetime | None:
    try:
        with Image.open(filepath) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, val in exif_data.items():
                    if TAGS.get(tag) == "DateTimeOriginal":
                        return datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"EXIF ошибка: {e}")
    return None
