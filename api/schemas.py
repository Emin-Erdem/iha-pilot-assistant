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