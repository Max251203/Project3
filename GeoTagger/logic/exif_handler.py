import os
from datetime import datetime, timedelta
import gpxpy
import piexif
from PySide6.QtWidgets import QMessageBox
import exiftool

from logic.time_sync import get_datetime_from_image
from logic.file_manager import SUPPORTED_EXTENSIONS
from logic.dialog_utils import confirm_overwrite_gps
from logic.logger import get_logger

# Инициализация логгера
logger = get_logger()


def process_images(folder_path: str, gpx_path: str, time_correction: str = "0:00") -> tuple[int, int]:
    """
    Основная функция: обрабатывает изображения, сопоставляет по времени, записывает координаты
    Возвращает: (сколько обновлено, всего)
    """
    logger.info(f"Начало обработки изображений в папке: {folder_path}")
    logger.info(f"Используется GPX-трек: {gpx_path}")
    logger.info(f"Поправка времени: {time_correction}")

    corrected_delta = parse_time_correction(time_correction)
    gpx_data = parse_gpx(gpx_path)

    if not gpx_data:
        logger.error("GPX-файл не содержит координаты")
        raise Exception("GPX-файл не содержит координаты")

    files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

    updated = 0
    total = len(files)
    global_prompt_state = None  # None / overwrite_all / skip_all

    logger.info(f"Найдено {total} файлов для обработки")

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        dt_original = get_datetime_from_image(filepath)

        if not dt_original:
            logger.warning(f"Не удалось получить время съёмки из {filename}")
            continue

        corrected_dt = dt_original + corrected_delta
        logger.info(
            f"Обработка {filename}: время съёмки {dt_original}, скорректированное {corrected_dt}")

        lat, lon = find_matching_coordinate(gpx_data, corrected_dt)

        if lat is None or lon is None:
            logger.warning(
                f"Не найдены координаты для {filename} на время {corrected_dt}")
            continue

        logger.info(f"Найдены координаты для {filename}: {lat:.6f}, {lon:.6f}")

        existing_gps = has_gps_in_exif(filepath)

        if existing_gps and global_prompt_state is None:
            logger.info(f"Файл {filename} уже содержит GPS-данные")
            result = confirm_overwrite_gps(filename)
            if result == "overwrite_all":
                global_prompt_state = "overwrite_all"
                logger.info("Выбрано: перезаписать все")
            elif result == "skip_all":
                global_prompt_state = "skip_all"
                logger.info("Выбрано: пропустить все")
            elif result == "overwrite":
                logger.info(f"Выбрано: перезаписать {filename}")
            elif result == "skip":
                logger.info(f"Выбрано: пропустить {filename}")
                continue
            elif result == "cancel":
                logger.info("Операция отменена пользователем")
                break

        if existing_gps and global_prompt_state == "skip_all":
            continue

        if write_gps_to_exif(filepath, lat, lon):
            updated += 1
            logger.success(
                f"Координаты записаны в {filename}: {lat:.6f}, {lon:.6f}")
        else:
            logger.error(f"Не удалось записать координаты в {filename}")

    logger.success(
        f"Обработка завершена: обновлено {updated} из {total} файлов")
    return updated, total


def parse_time_correction(text: str) -> timedelta:
    """Формат ввода: ±hh:mm"""
    try:
        sign = 1
        if text.startswith("-"):
            sign = -1
            text = text[1:]
        elif text.startswith("+"):
            text = text[1:]
        hours, minutes = map(int, text.strip().split(":"))
        return timedelta(hours=hours * sign, minutes=minutes * sign)
    except Exception as e:
        logger.error(f"Ошибка в формате поправки времени: {e}")
        raise ValueError("Неверный формат поправки времени. Используйте ±ч:мм")


def parse_gpx(gpx_path: str) -> list:
    """Парсит GPX-файл и возвращает список точек с временем и координатами"""
    logger.info(f"Парсинг GPX-файла: {gpx_path}")
    try:
        with open(gpx_path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        points.append({
                            # для простоты сравнения
                            "time": point.time.replace(tzinfo=None),
                            "lat": point.latitude,
                            "lon": point.longitude
                        })

        logger.info(f"Найдено {len(points)} точек в GPX-файле")
        return points
    except Exception as e:
        logger.error(f"Ошибка при парсинге GPX: {e}")
        return []


def find_matching_coordinate(gpx_data: list, timestamp: datetime):
    """Находит GPS координату, соответствующую времени с интерполяцией"""
    for i in range(len(gpx_data) - 1):
        pt1 = gpx_data[i]
        pt2 = gpx_data[i + 1]

        if pt1["time"] <= timestamp <= pt2["time"]:
            # Интерполяция
            total_diff = (pt2["time"] - pt1["time"]).total_seconds()
            if total_diff == 0:
                return pt1["lat"], pt1["lon"]

            factor = (timestamp - pt1["time"]).total_seconds() / total_diff
            lat = pt1["lat"] + (pt2["lat"] - pt1["lat"]) * factor
            lon = pt1["lon"] + (pt2["lon"] - pt1["lon"]) * factor
            return lat, lon

    # Если не нашли точку в диапазоне, ищем ближайшую
    if gpx_data:
        closest_point = min(gpx_data, key=lambda p: abs(
            (p["time"] - timestamp).total_seconds()))
        time_diff = abs((closest_point["time"] - timestamp).total_seconds())

        # Если разница меньше часа, используем эту точку
        if time_diff < 3600:
            logger.warning(
                f"Точное совпадение не найдено. Используется ближайшая точка ({time_diff:.1f} сек)")
            return closest_point["lat"], closest_point["lon"]

    logger.warning(f"Не найдены координаты для времени {timestamp}")
    return None, None


def deg_to_dms_rational(deg_float):
    """Преобразует float -> DMS -> rational для EXIF"""
    deg = int(deg_float)
    min_float = (deg_float - deg) * 60
    minute = int(min_float)
    sec = round((min_float - minute) * 60 * 10000)

    return (
        (deg, 1),
        (minute, 1),
        (sec, 10000)
    )


def write_gps_to_exif(filepath: str, lat: float, lon: float) -> bool:
    """Записывает координаты в EXIF — JPG через piexif, ARW через exiftool"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return write_gps_to_jpeg(filepath, lat, lon)
    elif ext == ".arw":
        return write_gps_with_exiftool(filepath, lat, lon)
    return False


def write_gps_to_jpeg(filepath: str, lat: float, lon: float) -> bool:
    """Запись GPS в JPEG через piexif"""
    try:
        exif_dict = piexif.load(filepath)

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: "N" if lat >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: deg_to_dms_rational(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: "E" if lon >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: deg_to_dms_rational(abs(lon)),
        }

        exif_dict["GPS"] = gps_ifd

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filepath)
        return True
    except Exception as e:
        logger.error(f"Ошибка при записи GPS в JPEG {filepath}: {e}")
        return False


def write_gps_with_exiftool(filepath: str, lat: float, lon: float) -> bool:
    """Запись GPS в ARW через exiftool"""
    try:
        with exiftool.ExifTool(executable="exiftool.exe") as et:
            cmds = [
                f"-GPSLatitude={abs(lat)}",
                f"-GPSLatitudeRef={'N' if lat >= 0 else 'S'}",
                f"-GPSLongitude={abs(lon)}",
                f"-GPSLongitudeRef={'E' if lon >= 0 else 'W'}",
                "-overwrite_original",
                filepath
            ]
            et.execute(*[cmd.encode("utf-8") for cmd in cmds])
        return True
    except Exception as e:
        logger.error(f"Ошибка при записи GPS в ARW {filepath}: {e}")
        return False


def has_gps_in_exif(filepath: str) -> bool:
    """Проверяет наличие GPS в EXIF"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        try:
            exif_dict = piexif.load(filepath)
            return bool(exif_dict.get("GPS"))
        except Exception as e:
            logger.error(f"Ошибка при проверке GPS в JPEG {filepath}: {e}")
            return False
    elif ext == ".arw":
        try:
            with exiftool.ExifTool(executable="exiftool.exe") as et:
                metadata = et.get_tags(
                    ["GPSLatitude", "GPSLongitude"], filepath)
                return "EXIF:GPSLatitude" in metadata or "EXIF:GPSLongitude" in metadata
        except Exception as e:
            logger.error(f"Ошибка при проверке GPS в ARW {filepath}: {e}")
            return False
    return False
