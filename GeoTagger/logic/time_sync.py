from datetime import datetime
import os
import subprocess
from PIL import Image
from PIL.ExifTags import TAGS

from logic.logger import get_logger
from logic.exif_utils import find_exiftool

logger = get_logger()


def get_datetime_from_image(filepath: str) -> datetime | None:
    ext = os.path.splitext(filepath)[1].lower()

    if ext in ['.jpg', '.jpeg']:
        try:
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                if not exif_data:
                    return None
                for tag, val in exif_data.items():
                    if TAGS.get(tag) == "DateTimeOriginal":
                        return datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"EXIF ошибка (JPG): {e}")
            return None

    elif ext == '.arw':
        exiftool = find_exiftool()
        if not exiftool:
            logger.error("❌ Не найден ExifTool для чтения даты из .ARW файла")
            return None
        try:
            result = subprocess.run(
                [exiftool, "-DateTimeOriginal", "-s3", filepath],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            dt_str = result.stdout.strip()
            if result.returncode != 0:
                logger.error(
                    f"ExifTool ошибка при чтении даты из {filepath}: {result.stderr.strip()}")
                return None
            if dt_str:
                logger.info(f"Дата из ARW {filepath}: {dt_str}")
                return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            logger.error(f"EXIF ошибка (ARW): {e}")
            return None

    return None
