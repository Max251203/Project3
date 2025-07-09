import os
from typing import List, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import QTableWidgetItem
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.arw', '.JPG', '.JPEG', '.ARW')


@dataclass
class ImageFileInfo:
    filepath: str
    filename: str
    datetime_original: Optional[str]
    gps_string: Optional[str]


def get_image_files(folder_path: str) -> List[ImageFileInfo]:
    result = []

    for file in os.listdir(folder_path):
        if file.lower().endswith(SUPPORTED_EXTENSIONS):
            full_path = os.path.join(folder_path, file)

            exif = read_exif(full_path)
            dt = exif.get("DateTimeOriginal", None)
            gps = extract_gps_string(exif)

            result.append(ImageFileInfo(
                filepath=full_path,
                filename=file,
                datetime_original=dt,
                gps_string=gps
            ))

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
        print(f"[read_exif] Ошибка при чтении {filepath}: {e}")

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
        print(f"[extract_gps_string] Ошибка: {e}")
    return None


def _convert_to_decimal(coord, ref) -> Optional[float]:
    """Преобразует координаты из формата EXIF DMS -> float"""
    if not coord or not ref:
        return None
    try:
        d = coord[0][0] / coord[0][1]
        m = coord[1][0] / coord[1][1]
        s = coord[2][0] / coord[2][1]
        decimal = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            decimal *= -1
        return decimal
    except Exception as e:
        print(f"[convert_to_decimal] Ошибка: {e}")
        return None
