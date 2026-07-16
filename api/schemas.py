from typing import Any

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """
    Represents a command received through the API.
    """

    type: str = Field(
        ...,
        description=(
            "Command type such as TAKEOFF, GOTO, "
            "HOVER, RETURN_HOME or LAND."
        )
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters required by the command."
    )


class MissionRequest(BaseModel):
    """
    Represents a mission received through the API.
    """

    name: str = Field(
        default="API Mission",
        min_length=1
    )

    commands: list[CommandRequest] = Field(
        ...,
        min_length=1
    )


class AIMissionRequest(BaseModel):
    """
    Represents a natural-language mission request.
    """

    instruction: str = Field(
        ...,
        min_length=3,
        description=(
            "Natural-language mission instruction."
        )
    )


class AIMissionResponse(BaseModel):
    """
    Represents a generated mission plan.
    """

    name: str = Field(
        default="AI Generated Mission",
        min_length=1
    )

    commands: list[CommandRequest] = Field(
        ...,
        min_length=1
    )


class CopilotTelemetry(BaseModel):
    """
    Represents the telemetry context sent to the copilot.
    """

    battery_level: float = Field(
        ...,
        ge=0,
        le=100
    )

    altitude: float

    position: dict[str, float] = Field(
        default_factory=dict
    )

    speed: float

    mode: str

    timestamp: str | None = None


class CopilotMissionContext(BaseModel):
    """
    Represents optional mission information
    provided to the copilot.
    """

    name: str | None = None

    status: str = "Waiting"

    commands: list[CommandRequest] = Field(
        default_factory=list
    )


class CopilotReportContext(BaseModel):
    """
    Represents an optional flight report summary
    provided to the copilot.
    """

    mission_name: str | None = None

    commands_executed: int | None = None

    distance_travelled: float | None = None

    max_altitude: float | None = None

    battery_used: float | None = None

    final_battery: float | None = None

    final_altitude: float | None = None

    final_position: list[float] | None = None

    flight_mode: str | None = None


class AICopilotRequest(BaseModel):
    """
    Represents a user question and the current
    drone system context.
    """

    question: str = Field(
        ...,
        min_length=2,
        description=(
            "The user's Turkish question for the AI copilot."
        )
    )

    telemetry: CopilotTelemetry

    mission: CopilotMissionContext | None = None

    report: CopilotReportContext | None = None


class AICopilotResponse(BaseModel):
    """
    Represents the AI copilot's Turkish answer.
    """

    answer: str = Field(
        ...,
        min_length=1
    )