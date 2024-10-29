from app.routers.dependencies import filter, db
from fastapi import APIRouter, status, HTTPException

from sqlalchemy import insert, select, func, delete, update

from app.schemas.hotels import HotelIn, HotelOut, HotelPatch
from app.models.hotels import HotelsOrm


router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get('/', response_model=list[HotelOut])
async def get_hotels(filter: filter, db: db):
    query = select(HotelsOrm)
    if filter.location:
        query = query.filter(func.lower(HotelsOrm.location).contains(filter.location.strip().lower()))
    if filter.title:
        query = query.filter(func.lower(HotelsOrm.title).contains(filter.title.strip().lower()))
    query = query.offset(filter.offset).limit(filter.limit)
    hotels = await db.scalars(query)
    return hotels


@router.post('/', response_model=HotelOut, status_code=status.HTTP_201_CREATED)
async def create_hotel(hotel: HotelIn, db: db):
    hotel = await db.scalar(insert(HotelsOrm).values(**hotel.model_dump()).returning(HotelsOrm))
    await db.commit()
    return hotel


@router.get('/{hotel_id}', response_model=HotelOut)
async def get_hotel(hotel_id: int, db: db):
    hotel = await db.scalar(select(HotelsOrm).where(HotelsOrm.id == hotel_id))
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='hotel not found'
        )
    return hotel


@router.put('/{hotel_id}', response_model=HotelOut)
async def edit_hotel(hotel_id: int, hotel: HotelIn, db: db):
    hotel_db = await db.scalar(select(HotelsOrm).where(HotelsOrm.id == hotel_id))
    if hotel_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='hotel not found'
        )
    hotel = await db.scalar(update(HotelsOrm).where(HotelsOrm.id == hotel_id).values(**hotel.model_dump()).returning(HotelsOrm))
    await db.commit()
    return hotel


@router.patch('/{hotel_id}', response_model=HotelOut)
async def partially_edit_hotel(hotel_id: int, hotel: HotelPatch, db: db):
    hotel_db = await db.scalar(select(HotelsOrm).where(HotelsOrm.id == hotel_id))
    if hotel_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='hotel not found'
        )
    hotel = await db.scalar(update(HotelsOrm).values(**hotel.model_dump(exclude_unset=True)).returning(HotelsOrm))
    await db.commit()
    return hotel


@router.delete('/{hotel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotel(hotel_id: int, db: db):
    hotel = await db.scalar(select(HotelsOrm).where(HotelsOrm.id == hotel_id))
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='hotel not found'
        )
    await db.execute(delete(HotelsOrm).where(HotelsOrm.id == hotel_id))
    await db.commit()