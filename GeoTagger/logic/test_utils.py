import os
import random
import shutil
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
import piexif
import gpxpy.gpx

from logic.logger import get_logger

logger = get_logger()


def create_test_dataset(output_folder: str) -> dict:
    """
    Создаёт тестовый набор данных: один GPX, 14 изображений (jpg+arw).
    Возвращает словарь с путём к gpx и списком созданных изображений
    """
    os.makedirs(output_folder, exist_ok=True)

    logger.info(f"Создание тестового набора в: {output_folder}")

    # 1. GPX: Старт 16:25 — 20 точек с шагом 1 минута
    gpx_path = os.path.join(output_folder, "test_track.gpx")
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    start_time = datetime(2025, 5, 19, 16, 25, 0)
    base_lat = 55.755
    base_lon = 37.617

    for i in range(20):
        time = start_time + timedelta(minutes=i)
        lat = base_lat + i * 0.001
        lon = base_lon + i * 0.001
        point = gpxpy.gpx.GPXTrackPoint(lat, lon, time=time)
        segment.points.append(point)

    with open(gpx_path, "w", encoding="utf-8") as f:
        f.write(gpx.to_xml())

    logger.success(f"Создан GPX с 20 точками: {gpx_path}")

    image_paths = []

    # 2. Изображения без GPS (5 шт.) в пределах времени GPX
    for i in range(5):
        dt = start_time + timedelta(minutes=i * 2)  # внутри трека
        img_path = create_image(
            output_folder, f"no_gps_{i+1}.jpg", dt, gps=False)
        image_paths.append(img_path)

    # # 3. Изображения с GPS (5 шт.) также в пределах трека
    # for i in range(5):
    #     dt = start_time + timedelta(minutes=i * 2 + 10)
    #     lat = base_lat + i * 0.001
    #     lon = base_lon + i * 0.001
    #     img_path = create_image(
    #         output_folder, f"with_gps_{i+1}.jpg", dt, gps=True, lat=lat, lon=lon)
    #     image_paths.append(img_path)
    # 3. Изображения с GPS (5 шт.) также в пределах трека
    for i in range(5):
        dt = start_time + timedelta(minutes=i * 2 + 10)
        # Разные координаты для каждого изображения
        lat = base_lat + i * 0.002  # Увеличиваем шаг для наглядности
        lon = base_lon + i * 0.002
        img_path = create_image(
            output_folder, f"with_gps_{i+1}.jpg", dt, gps=True, lat=lat, lon=lon)
        image_paths.append(img_path)

    # 4. Изображения с датой вне трека (до трека)
    for i in range(2):
        dt = start_time - timedelta(hours=1, minutes=i * 5)
        img_path = create_image(
            output_folder, f"outside_{i+1}.jpg", dt, gps=False)
        image_paths.append(img_path)

    # 5. Без EXIF даты вообще
    for i in range(2):
        img_path = os.path.join(output_folder, f"nodate_{i+1}.jpg")
        img = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"Image {i+1}", fill=(0, 0, 0))
        img.save(img_path)
        logger.info(f"Создано изображение без EXIF даты: {img_path}")
        image_paths.append(img_path)

    # 6. ARW-файлы (имитации): создаём на основе no_gps_1 и no_gps_2
    for i in range(2):
        src = os.path.join(output_folder, f"no_gps_{i+1}.jpg")
        dst = os.path.join(output_folder, f"no_gps_{i+1}.arw")
        shutil.copy(src, dst)
        logger.info(f"Создан имитированный ARW: {dst}")
        image_paths.append(dst)

    logger.success(f"Создано {len(image_paths)} тестовых изображений")

    return {
        "main_gpx_path": gpx_path,
        "image_paths": image_paths,
    }


def create_image(folder, name, dt: datetime, gps: bool = False, lat=None, lon=None):
    """
    Сохраняет изображение с EXIF датой, GPS по желанию
    """
    path = os.path.join(folder, name)
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    draw.text((10, 10), name, fill=(0, 0, 0), font=font)
    draw.text((10, 40), dt.strftime("%Y:%m:%d %H:%M:%S"),
              fill=(0, 0, 0), font=font)

    exif_dict = {"0th": {}, "Exif": {}}
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt.strftime(
        "%Y:%m:%d %H:%M:%S")

    if gps and lat is not None and lon is not None:
        exif_dict["GPS"] = {
            piexif.GPSIFD.GPSLatitudeRef: "N" if lat >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: float_to_rational_gps(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: "E" if lon >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: float_to_rational_gps(abs(lon)),
        }

    exif_bytes = piexif.dump(exif_dict)
    img.save(path, exif=exif_bytes)
    logger.info(f"Создано тестовое изображение: {path}")
    return path


def float_to_rational_gps(val):
    deg = int(val)
    min_float = (val - deg) * 60
    mins = int(min_float)
    secs = int((min_float - mins) * 60 * 100)
    return ((deg, 1), (mins, 1), (secs, 100))
