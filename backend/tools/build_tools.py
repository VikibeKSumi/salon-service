
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState 
from pydantic import AwareDatetime
from typing import Annotated
from datetime import date, datetime, time
from capability_services.capability_services import CapabilityService
from schemas.capability_services_schema import (
    CreateBookingInput, CancelBookingInput, RescheduleBookingInput,
    MyBookingsInput, GetFreeSlotsInput, HandoffInput
)


AGENT_TOOL_ACCESS = {
    "salon_service_agent": {
        "create_bookings",
        "cancel_bookings",
        "reschedule_bookings",
        "my_bookings",
        "get_free_slots",
        "list_services",
        "open_handoff"
    }
}

def build_tools(service: CapabilityService, agent=None):

    @tool
    def create_bookings(
        telegram_id: Annotated[int, InjectedState("telegram_id")],
        service_id: int,
        start_time: AwareDatetime,
    ):
        """create booking item on request"""
        return service.create_booking(request=CreateBookingInput(telegram_id=telegram_id, service_id=service_id, start_time=start_time)).model_dump(mode="json")
    

    @tool
    def cancel_bookings(
        telegram_id: Annotated[int, InjectedState("telegram_id")],
        booking_id: int,
    ):
        """cancel a booking item"""
        return service.cancel_booking(request=CancelBookingInput(telegram_id=telegram_id, booking_id=booking_id))
        

    @tool
    def reschedule_bookings(
        telegram_id: Annotated[int, InjectedState("telegram_id")],
        booking_id: int,
        new_start_time: AwareDatetime
    ):
        """to reschedule a booking"""
        return service.reschedule_booking(request=RescheduleBookingInput(telegram_id=telegram_id, booking_id=booking_id, new_start_time=new_start_time))

    @tool
    def my_bookings(
        telegram_id: Annotated[int, InjectedState("telegram_id")]
    ):
        """to check my booking"""
        return service.my_bookings(request=MyBookingsInput(telegram_id=telegram_id))

    @tool(args_schema=GetFreeSlotsInput)
    def get_free_slots(
        service_id: int,
        day: date,
    ):
        """get to see where the free slots are"""
        return service.get_free_slots(request=GetFreeSlotsInput(service_id=service_id, day=day))

    @tool
    def list_services():
        """get list of services provided and it's id"""
        return service.list_services()

    @tool
    def open_handoff(
        telegram_id: Annotated[int, InjectedState("telegram_id")] 
    ):
        """Hand off to a person when requested"""
        return service.open_handoff(request=HandoffInput(telegram_id=telegram_id))

    #build every tool list
    tools_list = [create_bookings, cancel_bookings, reschedule_bookings, my_bookings, get_free_slots, list_services, open_handoff]

    # agent registration
    if agent not in AGENT_TOOL_ACCESS:
        raise ValueError(f"Unknown agent: {agent}. Valid: {AGENT_TOOL_ACCESS}")

    # get tools 'name' allowed for the agent
    tools_allowed = AGENT_TOOL_ACCESS[agent]
    # get the tools from tools list
    tools_granted = [tool for tool in tools_list if tool.name in tools_allowed]

    # check again the allowed tools and retrieved tools are same in count number
    if len(tools_granted) != len(tools_allowed):
        missing = tools_allowed - {tool.name for tool in tools_granted}
        raise ValueError(f"AGENT_TOOL_ACCESS[{agent}] names unknown tools: {sorted(missing)}")

    return tools_granted