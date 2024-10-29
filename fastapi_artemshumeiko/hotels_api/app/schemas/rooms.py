from pydantic import BaseModel

class RoomIn(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int

class RoomOut(RoomIn):
    id: int
    hotel_id: int

class RoomPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None