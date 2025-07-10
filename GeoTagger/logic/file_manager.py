import os
import subprocess
from typing import List, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import QTableWidgetItem
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from logic.logger import get_logger
from logic.time_sync import get_datetime_from_image

logger = get_logger()

# Поддерживаемые расширения файлов
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.arw', '.JPG', '.JPEG', '.ARW')


@dataclass
class ImageFileInfo:
    filepath: str
    filename: str
    datetime_original: Optional[str]
    gps_string: Optional[str]


def get_image_files(folder_path: str, progress_callback=None) -> List[ImageFileInfo]:
    result = []

    files = [f for f in os.listdir(folder_path)
             if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    total_files = len(files)

    logger.info(f"Найдено {total_files} файлов в папке {folder_path}")

    for i, file in enumerate(files):
        if progress_callback:
            progress_callback.emit(int((i / total_files) * 100))

        full_path = os.path.join(folder_path, file)
        ext = os.path.splitext(full_path)[1].lower()

        try:
            # Расширение .arw обрабатывается отдельно
            if ext == '.arw':
                dt = get_datetime_from_image(full_path)

                # Получаем GPS координаты из ARW через exiftool
                gps = None
                from logic.config import get_exiftool_path
                exiftool = get_exiftool_path()
                if exiftool and os.path.exists(exiftool):
                    try:
                        cmd = [exiftool, "-n", "-GPSLatitude",
                               "-GPSLongitude", "-s3", full_path]
                        cwd = os.path.dirname(exiftool)
                        result_gps = subprocess.run(cmd, capture_output=True, text=True,
                                                    creationflags=subprocess.CREATE_NO_WINDOW, cwd=cwd)
                        if result_gps.returncode == 0 and result_gps.stdout.strip():
                            coords = result_gps.stdout.strip().split("\n")
                            if len(coords) >= 2:
                                lat = float(coords[0])
                                lon = float(coords[1])
                                gps = f"{lat:.6f}, {lon:.6f}"
                    except Exception as e:
                        logger.warning(
                            f"Ошибка при чтении GPS из ARW {file}: {e}")

                result.append(ImageFileInfo(
                    filepath=full_path,
                    filename=file,
                    datetime_original=dt.strftime(
                        "%Y:%m:%d %H:%M:%S") if dt else None,
                    gps_string=gps
                ))
                continue

            # Стандартная обработка JPG
            exif = read_exif(full_path)
            dt = exif.get("DateTimeOriginal", None)
            gps = extract_gps_string(exif)

            result.append(ImageFileInfo(
                filepath=full_path,
                filename=file,
                datetime_original=dt,
                gps_string=gps
            ))
        except Exception as e:
            logger.warning(f"Ошибка при чтении {file}: {e}")

    if progress_callback:
        progress_callback.emit(100)

    return result


def make_table_item(text: str) -> QTableWidgetItem:
    """Формирует ячейку таблицы из текста"""
    return QTableWidgetItem(text if text else "-")


def read_exif(filepath: str) -> dict:
    """Чтение EXIF-данных из изображения"""
    result = {}
    try:
        with Image.open(filepath) as img:
            exif_data = img._getexif()
            if not exif_data:
                return result

            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                result[decoded] = value

            # Если есть GPS — тоже вытащим
            gps_info = result.get("GPSInfo")
            if gps_info:
                gps_data = {}
                for t in gps_info:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = gps_info[t]
                result["GPSInfo"] = gps_data

    except Exception as e:
        logger.warning(f"Ошибка при чтении EXIF из {filepath}: {e}")

    return result


def extract_gps_string(exif: dict) -> Optional[str]:
    """Преобразует GPSInfo в строку широта, долгота"""
    gps_info = exif.get("GPSInfo", {})
    if not gps_info:
        return None

    try:
        lat = _convert_to_decimal(gps_info.get(
            "GPSLatitude"), gps_info.get("GPSLatitudeRef"))
        lon = _convert_to_decimal(gps_info.get(
            "GPSLongitude"), gps_info.get("GPSLongitudeRef"))
        if lat is not None and lon is not None:
            return f"{lat:.6f}, {lon:.6f}"
    except Exception as e:
        logger.warning(f"Ошибка при извлечении GPS: {e}")
    return None


def _convert_to_decimal(coord, ref) -> Optional[float]:
    """Преобразует координаты из формата EXIF DMS -> float"""
    if not coord or not ref:
        return None
    try:
        # Проверяем тип координат
        if isinstance(coord[0], tuple):
            d = coord[0][0] / coord[0][1]
            m = coord[1][0] / coord[1][1]
            s = coord[2][0] / coord[2][1]
        else:
            d, m, s = coord
        decimal = float(d) + float(m) / 60.0 + float(s) / 3600.0
        if ref in ['S', 'W']:
            decimal *= -1
        return decimal
    except Exception as e:
        logger.warning(f"Ошибка конвертации координат: {e}")
        return None
