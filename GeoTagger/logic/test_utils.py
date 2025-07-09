import os
import sys  # Добавляем импорт sys
import random
import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta
from math import cos, radians
from PIL import Image, ImageDraw, ImageFont
import piexif
import shutil  # Добавляем импорт shutil
from logic.logger import get_logger

# Инициализация логгера
logger = get_logger()


def create_test_gpx(output_path: str, start_time: datetime = None, duration_minutes: int = 60,
                    point_interval_seconds: int = 10, center_lat: float = 55.7558,
                    center_lon: float = 37.6173, radius_km: float = 1.0):
    """
    Создает тестовый GPX-файл с заданными параметрами

    Args:
        output_path: Путь для сохранения GPX-файла
        start_time: Время начала трека (если None, используется текущее время)
        duration_minutes: Продолжительность трека в минутах
        point_interval_seconds: Интервал между точками в секундах
        center_lat: Центральная широта для генерации точек
        center_lon: Центральная долгота для генерации точек
        radius_km: Радиус в километрах для генерации точек

    Returns:
        Путь к созданному GPX-файлу
    """
    # Если время начала не указано, используем текущее
    if start_time is None:
        start_time = datetime(2025, 5, 19, 16, 25, 45)

    # Создаем GPX-объект
    gpx = gpxpy.gpx.GPX()

    # Создаем трек
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)

    # Создаем сегмент
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    # Рассчитываем количество точек
    total_seconds = duration_minutes * 60
    num_points = total_seconds // point_interval_seconds

    # Генерируем точки
    for i in range(num_points):
        # Рассчитываем время для точки
        point_time = start_time + timedelta(seconds=i * point_interval_seconds)

        # Генерируем случайное смещение от центра
        # Конвертируем км в градусы (приблизительно)
        lat_offset = (random.random() * 2 - 1) * radius_km / \
            111.0  # 1 градус широты ~ 111 км
        lon_offset = (random.random() * 2 - 1) * radius_km / \
            (111.0 * cos(radians(center_lat)))  # Поправка на широту

        # Рассчитываем координаты точки
        lat = center_lat + lat_offset
        lon = center_lon + lon_offset

        # Создаем точку
        point = gpxpy.gpx.GPXTrackPoint(lat, lon, time=point_time)
        segment.points.append(point)

    # Сохраняем GPX-файл
    with open(output_path, 'w') as f:
        f.write(gpx.to_xml())

    logger.info(
        f"Создан тестовый GPX-файл: {output_path} с {num_points} точками")
    return output_path


def create_simple_gpx(output_path: str):
    """
    Создает простой GPX-файл с несколькими точками по прямой линии

    Args:
        output_path: Путь для сохранения GPX-файла

    Returns:
        Путь к созданному GPX-файлу
    """
    # Создаем GPX-объект
    gpx = gpxpy.gpx.GPX()

    # Создаем трек
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)

    # Создаем сегмент
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    # Базовое время и координаты
    base_time = datetime(2025, 5, 19, 16, 25, 45)  # Время в UTC
    base_lat = 55.7558
    base_lon = 37.6173

    # Добавляем точки
    for i in range(20):
        point_time = base_time + timedelta(minutes=i*5)
        lat = base_lat + (i * 0.001)
        lon = base_lon + (i * 0.001)

        point = gpxpy.gpx.GPXTrackPoint(lat, lon, time=point_time)
        segment.points.append(point)

    # Сохраняем GPX-файл
    with open(output_path, 'w') as f:
        f.write(gpx.to_xml())

    logger.info(f"Создан простой GPX-файл: {output_path}")
    return output_path


def create_complex_gpx(output_path: str):
    """
    Создает сложный GPX-файл с несколькими треками и сегментами

    Args:
        output_path: Путь для сохранения GPX-файла

    Returns:
        Путь к созданному GPX-файлу
    """
    # Создаем GPX-объект
    gpx = gpxpy.gpx.GPX()

    # Создаем первый трек
    track1 = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track1)

    # Создаем сегмент для первого трека
    segment1 = gpxpy.gpx.GPXTrackSegment()
    track1.segments.append(segment1)

    # Базовое время и координаты для первого трека
    base_time = datetime(2025, 5, 19, 16, 25, 45)  # Время в UTC
    base_lat = 55.7558
    base_lon = 37.6173

    # Добавляем точки в первый сегмент
    for i in range(10):
        point_time = base_time + timedelta(minutes=i*5)
        lat = base_lat + (i * 0.001)
        lon = base_lon + (i * 0.001)

        point = gpxpy.gpx.GPXTrackPoint(lat, lon, time=point_time)
        segment1.points.append(point)

    # Создаем второй трек
    track2 = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track2)

    # Создаем сегмент для второго трека
    segment2 = gpxpy.gpx.GPXTrackSegment()
    track2.segments.append(segment2)

    # Базовое время и координаты для второго трека
    base_time2 = base_time + timedelta(hours=1)
    base_lat2 = 55.7658
    base_lon2 = 37.6273

    # Добавляем точки во второй сегмент
    for i in range(10):
        point_time = base_time2 + timedelta(minutes=i*5)
        lat = base_lat2 - (i * 0.001)
        lon = base_lon2 - (i * 0.001)

        point = gpxpy.gpx.GPXTrackPoint(lat, lon, time=point_time)
        segment2.points.append(point)

    # Сохраняем GPX-файл
    with open(output_path, 'w') as f:
        f.write(gpx.to_xml())

    logger.info(f"Создан сложный GPX-файл: {output_path}")
    return output_path


def analyze_gpx_file(gpx_path: str):
    """Анализирует GPX-файл и выводит информацию о нем"""
    try:
        with open(gpx_path, 'r') as f:
            gpx = gpxpy.parse(f)

        # Собираем статистику
        track_count = len(gpx.tracks)
        segment_count = sum(len(track.segments) for track in gpx.tracks)
        point_count = sum(sum(len(segment.points)
                          for segment in track.segments) for track in gpx.tracks)

        # Собираем все точки с временем
        points_with_time = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        points_with_time.append(point)

        # Сортируем по времени
        points_with_time.sort(key=lambda p: p.time)

        # Выводим информацию
        if points_with_time:
            start_time = points_with_time[0].time
            end_time = points_with_time[-1].time
            duration = end_time - start_time

            logger.info(f"GPX-файл: {gpx_path}")
            logger.info(
                f"Треков: {track_count}, сегментов: {segment_count}, точек: {point_count}")
            logger.info(f"Точек с временем: {len(points_with_time)}")
            logger.info(f"Начало: {start_time}, конец: {end_time}")
            logger.info(f"Продолжительность: {duration}")

            return {
                "track_count": track_count,
                "segment_count": segment_count,
                "point_count": point_count,
                "points_with_time": len(points_with_time),
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration
            }
        else:
            logger.warning(f"GPX-файл {gpx_path} не содержит точек с временем")
            return None

    except Exception as e:
        logger.error(f"Ошибка при анализе GPX-файла {gpx_path}: {e}")
        return None


def create_test_images(output_folder: str, count: int = 5, base_time: datetime = None, with_gps: bool = False):
    """
    Создает тестовые изображения с EXIF-данными

    Args:
        output_folder: Папка для сохранения изображений
        count: Количество изображений
        base_time: Базовое время для изображений (если None, используется время из GPX)
        with_gps: Добавлять ли GPS-координаты в EXIF

    Returns:
        Список путей к созданным изображениям
    """
    os.makedirs(output_folder, exist_ok=True)

    if base_time is None:
        base_time = datetime(2025, 5, 19, 16, 30, 0)

    image_paths = []

    for i in range(count):
        # Создаем время для изображения
        image_time = base_time + timedelta(minutes=i*5)
        image_time_str = image_time.strftime("%Y:%m:%d %H:%M:%S")

        # Создаем изображение
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))

        # Добавляем текст на изображение
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        draw.text((10, 10), f"Test Image {i+1}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), f"Time: {image_time_str}",
                  fill=(0, 0, 0), font=font)

        # Создаем EXIF-данные
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}}
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = image_time_str

        # Добавляем GPS-координаты, если нужно
        if with_gps:
            # Базовые координаты
            lat = 55.7558 + (i * 0.001)
            lon = 37.6173 + (i * 0.001)

            # Преобразуем координаты в формат EXIF
            lat_ref = "N" if lat >= 0 else "S"
            lon_ref = "E" if lon >= 0 else "W"

            lat_deg = int(abs(lat))
            lat_min = int((abs(lat) - lat_deg) * 60)
            lat_sec = int(((abs(lat) - lat_deg) * 60 - lat_min) * 60 * 100)

            lon_deg = int(abs(lon))
            lon_min = int((abs(lon) - lon_deg) * 60)
            lon_sec = int(((abs(lon) - lon_deg) * 60 - lon_min) * 60 * 100)

            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = (
                (lat_deg, 1), (lat_min, 1), (lat_sec, 100))
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lon_ref
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = (
                (lon_deg, 1), (lon_min, 1), (lon_sec, 100))

        # Сохраняем изображение
        filename = f"test_image_{i+1}.jpg"
        if with_gps:
            filename = f"test_image_with_gps_{i+1}.jpg"

        filepath = os.path.join(output_folder, filename)
        exif_bytes = piexif.dump(exif_dict)
        img.save(filepath, exif=exif_bytes)

        image_paths.append(filepath)
        logger.info(
            f"Создано тестовое изображение: {filename} с датой {image_time_str}")

    return image_paths


def create_test_dataset(output_folder: str, gpx_filename: str = "test_track.gpx",
                        image_count: int = 5, start_time: datetime = None):
    """
    Создает тестовый набор данных: GPX-файл и изображения с EXIF-данными

    Args:
        output_folder: Папка для сохранения тестовых данных
        gpx_filename: Имя GPX-файла
        image_count: Количество тестовых изображений
        start_time: Время начала трека (если None, используется текущее время)

    Returns:
        Словарь с информацией о созданных файлах
    """
    # Создаем выходную папку
    os.makedirs(output_folder, exist_ok=True)

    # Если время начала не указано, используем текущее
    if start_time is None:
        start_time = datetime(2025, 5, 19, 16, 25, 45)

    logger.info(f"Создание тестового набора данных в папке: {output_folder}")

    # Создаем GPX-файлы
    gpx_paths = []

    # Простой GPX-файл
    simple_gpx_path = os.path.join(output_folder, "simple_" + gpx_filename)
    create_simple_gpx(simple_gpx_path)
    gpx_paths.append(simple_gpx_path)

    # Сложный GPX-файл
    complex_gpx_path = os.path.join(output_folder, "complex_" + gpx_filename)
    create_complex_gpx(complex_gpx_path)
    gpx_paths.append(complex_gpx_path)

    # Случайный GPX-файл
    random_gpx_path = os.path.join(output_folder, "random_" + gpx_filename)
    create_test_gpx(random_gpx_path, start_time=start_time,
                    duration_minutes=60, point_interval_seconds=30)
    gpx_paths.append(random_gpx_path)

    # Анализируем GPX-файлы
    gpx_info = {}
    for gpx_path in gpx_paths:
        gpx_info[os.path.basename(gpx_path)] = analyze_gpx_file(gpx_path)

    # Создаем изображения
    image_paths = []

    # Изображения без GPS
    images_without_gps = create_test_images(
        output_folder,
        count=image_count,
        base_time=start_time + timedelta(minutes=5),
        with_gps=False
    )
    image_paths.extend(images_without_gps)

    # Изображения с GPS
    images_with_gps = create_test_images(
        output_folder,
        count=image_count,
        base_time=start_time + timedelta(minutes=5),
        with_gps=True
    )
    image_paths.extend(images_with_gps)

    # Создаем изображения вне диапазона трека
    images_outside_range = create_test_images(
        output_folder,
        count=2,
        base_time=start_time - timedelta(hours=2),
        with_gps=False
    )
    image_paths.extend(images_outside_range)

    # Создаем изображения с некорректным временем
    images_invalid_time = []
    for i in range(2):
        # Создаем изображение без EXIF-даты
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        draw.text(
            (10, 10), f"Test Image Invalid {i+1}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), "No EXIF date", fill=(0, 0, 0), font=font)

        filename = f"test_image_invalid_{i+1}.jpg"
        filepath = os.path.join(output_folder, filename)
        img.save(filepath)

        images_invalid_time.append(filepath)
        logger.info(f"Создано тестовое изображение без EXIF-даты: {filename}")

    image_paths.extend(images_invalid_time)

    # Создаем ARW-подобные файлы (просто переименовываем JPG в ARW)
    arw_paths = []
    for i, jpg_path in enumerate(images_without_gps[:2]):
        arw_path = jpg_path.replace(".jpg", ".arw")
        # Копируем файл
        import shutil
        shutil.copy(jpg_path, arw_path)
        arw_paths.append(arw_path)
        logger.info(f"Создан тестовый ARW-файл: {os.path.basename(arw_path)}")

    image_paths.extend(arw_paths)

    logger.success(f"Создан тестовый набор данных в папке: {output_folder}")
    logger.success(f"Создано {len(gpx_paths)} GPX-файлов")
    logger.success(f"Создано {len(image_paths)} тестовых изображений")

    return {
        "gpx_paths": gpx_paths,
        "image_paths": image_paths,
        "gpx_info": gpx_info,
        "main_gpx_path": simple_gpx_path  # Возвращаем простой GPX как основной
    }
