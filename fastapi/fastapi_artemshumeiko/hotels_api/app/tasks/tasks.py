import asyncio
from PIL import Image
import os
from app.schemas.bookings import BookingOut
from app.database import async_session_maker_null_pool
from app.tasks.celery_app import celery_instance
from sqlalchemy import select
from app.models import BookingsOrm
from datetime import date
import logging


@celery_instance.task
def resize_image(image_path: str):
    logging.debug(f"Вызывается функция image_path с {image_path=}")
    sizes = [1000, 500, 200]
    output_folder = "/home/evalshine/backend/hotelsapi_media"

    # Открываем изображение
    img = Image.open(image_path)

    # Получаем имя файла и его расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    # Проходим по каждому размеру
    for size in sizes:
        # Сжимаем изображение
        img_resized = img.resize(
            (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
        )

        # Формируем имя нового файла
        new_file_name = f"{name}_{size}px{ext}"

        # Полный путь для сохранения
        output_path = os.path.join(output_folder, new_file_name)

        # Сохраняем изображение
        img_resized.save(output_path)

    logging.info(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")


async def get_bookings_with_today_checkin_helper():
    async with async_session_maker_null_pool() as session:
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())
        res = await session.execute(query)
        print([BookingOut.model_validate(el.__dict__) for el in res.scalars().all()])


@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
