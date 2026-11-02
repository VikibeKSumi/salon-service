from capability_services.repository.postgres_repository import PostgresRepository
from schemas.capability_services_schema import (
    ServiceResult, Service, Customer, Booking, Handoff,
    GetOrCreateCustomerInput, GetFreeSlotsInput, CreateBookingInput, MyBookingsInput,
    CancelBookingInput, RescheduleBookingInput, HandoffInput,
)
from psycopg.errors import ExclusionViolation
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Kolkata")
STEP = timedelta(minutes=15)


class CapabilityService:
    def __init__(self, repo: PostgresRepository):
        self.repo = repo

    # ==services===
    def list_services(self) -> ServiceResult[list[Service]]:
        services = self.repo.list_services()
        if not services:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="No services available")
        return ServiceResult(success=True, result_code="OK", payload=services)

    # ==customers===
    def get_or_create_customer(self, request: GetOrCreateCustomerInput) -> ServiceResult[Customer]:
        customer = self.repo.upsert_customer(request.telegram_id, request.name)
        return ServiceResult(success=True, result_code="OK", payload=customer)

    # ==slots===
    def get_free_slots(self, request: GetFreeSlotsInput) -> ServiceResult[list[datetime]]:
        return self._free_slots(request)

    def _free_slots(self, request: GetFreeSlotsInput, exclude_booking_id: int | None = None) -> ServiceResult[list[datetime]]:
        # exclude_booking_id: when rescheduling, the booking's own current time doesn't count as busy
        service = self.repo.get_service(request.service_id)
        if service is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="Service not found")

        hours = self.repo.get_hours(request.day.weekday())
        if hours is None or self.repo.is_holiday(request.day):
            return ServiceResult(success=True, result_code="CLOSED", payload=[], message="Closed that day")

        open_at = datetime.combine(request.day, hours.open_time, tzinfo=TZ)
        close_at = datetime.combine(request.day, hours.close_time, tzinfo=TZ)
        duration = timedelta(minutes=service.duration_min)
        busy = self.repo.get_busy(open_at, close_at, exclude_booking_id)
        now = datetime.now(TZ)

        slots = []
        start = open_at
        while start + duration <= close_at:
            end = start + duration
            overlaps = any(start < b.end_time and end > b.start_time for b in busy)
            if start > now and not overlaps:
                slots.append(start)
            start += STEP
        return ServiceResult(success=True, result_code="OK", payload=slots)

    def _check_slot(self, service_id: int, start: datetime, exclude_booking_id: int | None = None) -> ServiceResult | None:
        """Return a failed result if `start` isn't a free slot, else None."""
        day = start.astimezone(TZ).date()
        free = self._free_slots(GetFreeSlotsInput(service_id=service_id, day=day), exclude_booking_id)
        if not free.success:
            return ServiceResult(success=False, result_code=free.result_code, message=free.message)
        if free.result_code == "CLOSED":
            return ServiceResult(success=False, result_code="CLOSED", message=free.message)
        if start not in free.payload:
            return ServiceResult(success=False, result_code="SLOT_TAKEN", message="That time isn't available")
        return None

    # ==bookings===
    def create_booking(self, request: CreateBookingInput) -> ServiceResult[Booking]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="Customer not found")

        failed = self._check_slot(request.service_id, request.start_time)
        if failed:
            return failed

        service = self.repo.get_service(request.service_id)
        end = request.start_time + timedelta(minutes=service.duration_min)
        try:
            booking = self.repo.insert_booking(customer.id, service.id, request.start_time, end)
        except ExclusionViolation:
            return ServiceResult(success=False, result_code="SLOT_TAKEN", message="Someone just booked that time")
        return ServiceResult(success=True, result_code="OK", payload=booking)

    def my_bookings(self, request: MyBookingsInput) -> ServiceResult[list[Booking]]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=True, result_code="OK", payload=[])
        return ServiceResult(success=True, result_code="OK", payload=self.repo.get_upcoming_bookings(customer.id))

    def cancel_booking(self, request: CancelBookingInput) -> ServiceResult[Booking]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="Customer not found")

        booking = self.repo.cancel_booking(request.booking_id, customer.id)
        if booking is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="No upcoming booking with that id")
        return ServiceResult(success=True, result_code="OK", payload=booking)

    def reschedule_booking(self, request: RescheduleBookingInput) -> ServiceResult[Booking]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="Customer not found")

        current = self.repo.get_upcoming_booking(request.booking_id, customer.id)
        if current is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="No upcoming booking with that id")
        if request.new_start_time == current.start_time:
            return ServiceResult(success=False, result_code="INVALID_INPUT", message="That's already the booked time")

        failed = self._check_slot(current.service_id, request.new_start_time, exclude_booking_id=current.id)
        if failed:
            return failed

        duration = current.end_time - current.start_time
        try:
            booking = self.repo.move_booking(current.id, customer.id, request.new_start_time, request.new_start_time + duration)
        except ExclusionViolation:
            return ServiceResult(success=False, result_code="SLOT_TAKEN", message="Someone just booked that time")
        if booking is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="No upcoming booking with that id")
        return ServiceResult(success=True, result_code="OK", payload=booking)

    # ==handoffs===
    def open_handoff(self, request: HandoffInput) -> ServiceResult[Handoff]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=False, result_code="NOT_FOUND", message="Customer not found")
        return ServiceResult(success=True, result_code="OK", payload=self.repo.open_handoff(customer.id))

    def is_handoff_active(self, request: HandoffInput) -> ServiceResult[bool]:
        customer = self.repo.get_customer(request.telegram_id)
        if customer is None:
            return ServiceResult(success=True, result_code="OK", payload=False)
        return ServiceResult(success=True, result_code="OK", payload=self.repo.has_open_handoff(customer.id))
