import os
import subprocess
from datetime import datetime, timedelta
import gpxpy
import piexif

from logic.time_sync import get_datetime_from_image
from logic.exif_utils import find_exiftool
from logic.file_manager import SUPPORTED_EXTENSIONS
from logic.dialog_utils import confirm_overwrite_gps
from logic.logger import get_logger

logger = get_logger()


def process_images(folder_path: str, gpx_path: str, time_correction: str = "0:00", confirm_callback=None) -> tuple[int, int]:
    """
    Обрабатывает изображения, добавляя GPS-координаты из GPX-файла.

    Args:
        folder_path: Путь к папке с изображениями
        gpx_path: Путь к GPX-файлу
        time_correction: Поправка времени в формате "±ч:мм"
        confirm_callback: Функция для подтверждения перезаписи GPS

    Returns:
        (обновлено, всего): Количество обновленных файлов и общее количество
    """
    logger.info(f"Начата обработка изображений в: {folder_path}")
    logger.info(f"Используем GPX: {gpx_path}")
    logger.info(f"Поправка времени: {time_correction}")

    corrected_delta = parse_time_correction(time_correction)
    gpx_data = parse_gpx(gpx_path)
    if not gpx_data:
        raise Exception("GPX-файл не содержит координат")

    files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    total = len(files)
    updated = 0
    global_action = None  # overwrite_all, skip_all

    logger.info(f"Найдено {total} изображений для обработки")

    for i, filename in enumerate(files):
        filepath = os.path.join(folder_path, filename)
        dt_original = get_datetime_from_image(filepath)

        if not dt_original:
            logger.warning(f"{filename} — отсутствует дата съёмки")
            continue

        corrected_dt = dt_original + corrected_delta
        lat, lon = find_matching_coordinate(gpx_data, corrected_dt)

        if lat is None or lon is None:
            logger.warning(
                f"{filename} — координаты не найдены на {corrected_dt}")
            continue

        logger.info(f"{filename}: координаты — {lat:.6f}, {lon:.6f}")

        has_gps = has_gps_in_exif(filepath)

        if has_gps:
            if global_action is None:
                if confirm_callback:
                    action = confirm_callback(filename)
                else:
                    action = "skip"

                if action == "cancel":
                    logger.warning("Пользователь отменил обработку")
                    # Немедленно прерываем обработку
                    return updated, total
                elif action == "overwrite":
                    pass  # Продолжаем запись
                elif action == "skip":
                    continue
                elif action == "overwrite_all":
                    global_action = "overwrite_all"
                elif action == "skip_all":
                    global_action = "skip_all"
                    continue
            elif global_action == "skip_all":
                continue

        if write_gps_to_exif(filepath, lat, lon):
            updated += 1
            logger.success(f"Записано: {filename} — {lat:.6f}, {lon:.6f}")
        else:
            logger.error(f"Не удалось записать EXIF в {filename}")

    return updated, total


def parse_time_correction(text: str) -> timedelta:
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
        logger.error(f"Ошибка в формате смещения времени: {e}")
        raise


def parse_gpx(gpx_path: str) -> list:
    try:
        with open(gpx_path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        points.append({
                            "time": point.time.replace(tzinfo=None),
                            "lat": point.latitude,
                            "lon": point.longitude
                        })
        logger.info(f"Извлечено {len(points)} точек из GPX")
        return points
    except Exception as e:
        logger.error(f"Ошибка GPX парсинга: {e}")
        return []


def find_matching_coordinate(gpx_data: list, timestamp: datetime):
    for i in range(len(gpx_data) - 1):
        pt1, pt2 = gpx_data[i], gpx_data[i + 1]
        if pt1["time"] <= timestamp <= pt2["time"]:
            total_diff = (pt2["time"] - pt1["time"]).total_seconds()
            factor = (timestamp - pt1["time"]).total_seconds() / total_diff
            lat = pt1["lat"] + (pt2["lat"] - pt1["lat"]) * factor
            lon = pt1["lon"] + (pt2["lon"] - pt1["lon"]) * factor
            return lat, lon
    if gpx_data:
        closest = min(gpx_data, key=lambda p: abs(
            (p["time"] - timestamp).total_seconds()))
        diff_sec = abs((closest["time"] - timestamp).total_seconds())
        if diff_sec < 3600:
            logger.warning(
                f"Использована ближайшая точка ({diff_sec:.0f} сек)")
            return closest["lat"], closest["lon"]
    return None, None


def deg_to_dms_rational(deg_float):
    deg = int(deg_float)
    min_float = (deg_float - deg) * 60
    minute = int(min_float)
    sec = round((min_float - minute) * 60 * 10000)
    return ((deg, 1), (minute, 1), (sec, 10000))


def write_gps_to_exif(filepath: str, lat: float, lon: float) -> bool:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return write_gps_to_jpeg(filepath, lat, lon)
    elif ext == ".arw":
        return write_gps_with_exiftool(filepath, lat, lon)
    return False


def write_gps_to_jpeg(filepath: str, lat: float, lon: float) -> bool:
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
        logger.error(f"Ошибка записи GPS в JPEG {filepath}: {e}")
        return False


def write_gps_with_exiftool(filepath: str, lat: float, lon: float) -> bool:
    from logic.config import get_exiftool_path

    # Используем СОХРАНЁННЫЙ путь, а не ищем заново
    exiftool = get_exiftool_path()

    if not exiftool or not os.path.exists(exiftool):
        logger.error("ExifTool не найден для записи в ARW")
        return False

    try:
        cmd = [
            exiftool,
            f"-GPSLatitude={abs(lat)}",
            f"-GPSLatitudeRef={'N' if lat >= 0 else 'S'}",
            f"-GPSLongitude={abs(lon)}",
            f"-GPSLongitudeRef={'E' if lon >= 0 else 'W'}",
            "-overwrite_original",
            filepath
        ]

        # Используем папку exiftool как рабочую директорию
        cwd = os.path.dirname(exiftool)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=cwd
        )

        if result.returncode != 0:
            logger.error(f"ExifTool ошибка: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        logger.error(f"Ошибка при записи в ARW {filepath}: {e}")
        return False


def has_gps_in_exif(filepath: str) -> bool:
    from logic.config import get_exiftool_path

    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        try:
            import piexif
            exif_dict = piexif.load(filepath)
            return bool(exif_dict.get("GPS"))
        except Exception:
            return False
    elif ext == '.arw':
        # Используем СОХРАНЁННЫЙ путь
        exiftool = get_exiftool_path()

        if not exiftool or not os.path.exists(exiftool):
            return False
        try:
            cmd = [exiftool, "-s", "-GPSLatitude", "-GPSLongitude", filepath]
            cwd = os.path.dirname(exiftool)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=cwd
            )

            return "GPSLatitude" in result.stdout or "GPSLongitude" in result.stdout
        except Exception:
            return False
    return False


def find_exiftool():
    import os
    from logic.logger import get_logger
    logger = get_logger()

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for root, dirs, files in os.walk(project_dir):
        for name in ["exiftool.exe", "exiftool(-k).exe", "exiftool"]:
            if name in files:
                return os.path.join(root, name)

    # Проверка в PATH
    try:
        result = subprocess.run(["exiftool", "-ver"],
                                capture_output=True, text=True, check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        logger.info(f"ExifTool найден в PATH (v{result.stdout.strip()})")
        return "exiftool"
    except Exception as e:
        logger.error(
            "ExifTool не найден! Убедитесь, что в папке с программой есть exiftool.exe")
        return None
