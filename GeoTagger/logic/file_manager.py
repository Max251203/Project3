import os
from typing import List, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import QTableWidgetItem
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from logic.logger import get_logger

# Инициализация логгера
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
    """Получает список файлов изображений с EXIF-данными"""
    result = []

    # Получаем список файлов
    files = [f for f in os.listdir(
        folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    total_files = len(files)

    logger.info(f"Найдено {total_files} файлов в папке {folder_path}")

    for i, file in enumerate(files):
        # Обновляем прогресс
        if progress_callback:
            progress_callback.emit(int((i / total_files) * 100))

        full_path = os.path.join(folder_path, file)

        try:
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

    # Финальный прогресс
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
        d = coord[0][0] / coord[0][1]
        m = coord[1][0] / coord[1][1]
        s = coord[2][0] / coord[2][1]
        decimal = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            decimal *= -1
        return decimal
    except Exception as e:
        logger.warning(f"Ошибка при конвертации координат: {e}")
        return None


def create_test_images(output_folder: str, count: int = 5, base_datetime: str = "2025:05:19 16:25:00"):
    """Создает тестовые изображения с EXIF-данными для тестирования"""
    import piexif
    from datetime import datetime, timedelta

    os.makedirs(output_folder, exist_ok=True)

    # Парсим базовую дату
    base_dt = datetime.strptime(base_datetime, "%Y:%m:%d %H:%M:%S")

    for i in range(count):
        # Создаем новую дату с интервалом в 5 минут
        dt = base_dt + timedelta(minutes=i*5)
        dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")

        # Создаем новое изображение
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))

        # Создаем EXIF-данные
        exif_dict = {"0th": {}, "Exif": {}}
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_str

        # Сохраняем изображение
        filename = f"test_image_{i+1}.jpg"
        filepath = os.path.join(output_folder, filename)
        exif_bytes = piexif.dump(exif_dict)
        img.save(filepath, exif=exif_bytes)

        logger.info(
            f"Создано тестовое изображение: {filename} с датой {dt_str}")

    return count
