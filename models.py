from pydantic import BaseModel


# Pydantic models
class Floor(BaseModel):
    id: int
    name: str


class Seat(BaseModel):
    id: int
    floor_id: int
    number: int
    is_occupied: bool


class Statistic(BaseModel):
    total_capacity: int
    average_occupancy_time: float
    current_occupancy_rate: float


class InOut(BaseModel):
    timestamp: int
    students_in: int
    students_out: int
