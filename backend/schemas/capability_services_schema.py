from pydantic import AwareDatetime, BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional, Literal
from datetime import date, datetime, time

T = TypeVar("T")

class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

class OutputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


ResultCode = Literal["OK", "NOT_FOUND", "CLOSED", "SLOT_TAKEN", "INVALID_INPUT"]

class ServiceResult(OutputModel, Generic[T]):
    success: bool
    result_code: ResultCode
    payload: Optional[T] = None
    message: str = ""


# ==input schemas===
class GetOrCreateCustomerInput(InputModel):
    telegram_id: int
    name: Optional[str] = None

class GetFreeSlotsInput(InputModel):
    service_id: int
    day: date

class CreateBookingInput(InputModel):
    telegram_id: int
    service_id: int
    start_time: AwareDatetime        # must include a timezone

class MyBookingsInput(InputModel):
    telegram_id: int

class CancelBookingInput(InputModel):
    telegram_id: int
    booking_id: int

class RescheduleBookingInput(InputModel):
    telegram_id: int
    booking_id: int
    new_start_time: AwareDatetime

class HandoffInput(InputModel):
    telegram_id: int


# ==output schemas===
class Service(OutputModel):
    id: int
    name: str
    duration_min: int
    price: int

class Customer(OutputModel):
    id: int
    telegram_id: int
    name: Optional[str] = None
    phone: Optional[str] = None

class Booking(OutputModel):
    id: int
    customer_id: int
    service_id: int
    service_name: str
    start_time: datetime
    end_time: datetime
    status: str

class Handoff(OutputModel):
    id: int
    customer_id: int
    status: str

class BusyInterval(OutputModel):
    start_time: datetime
    end_time: datetime

class Hours(OutputModel):
    open_time: time
    close_time: time
