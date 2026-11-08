from fastapi import APIRouter, Depends
from pydantic import AwareDatetime
from schemas.io_model_config import InputModel
from routes.dependencies import get_current_user


owner_router = APIRouter(prefix="/owner", dependencies=[Depends(get_current_user)])

class RescheduleBody(InputModel):
    new_start_time: AwareDatetime

# booking table
@owner_router.get("/bookings?date=")
def get_bookings():
    return {
        "return": "pending get_booking implementation"
    }

@owner_router.post("/bookings/{id}/cancel")
def cancel_booking():
    return {
            "return": "pending cancel_booking implementation"
    }

# services table
@owner_router.get("/services")
def get_services():
    return {
        "return": "pending get_services implementation"
    }
# customers table
@owner_router.get("/customers")
def get_customers():
    return {
        "return": "pending get_customers implementation"
    }

# holidays table
@owner_router.get("/holidays")
def get_holidays():
    return {
        "return": "pending get_holidays implementation"
    }

# business_hours table
@owner_router.get("/business_hours")
def get_business_hours():
    return {
        "return": "pending get_business_hours implementation"
    }

# handoff table
@owner_router.get("/handoff")
def get_handoff():
    return {
        "return": "pending get_handoff implementation"
    }

@owner_router.post("/handoff")
def cancel_handoff():
    return {
        "return" : "pending cance_handoff implementation"
    }

