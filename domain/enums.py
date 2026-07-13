from enum import Enum


class FlightMode(Enum):
    """
    Represents the flight modes of the drone.
    """

    IDLE = "IDLE"
    TAKING_OFF = "TAKING_OFF"
    FLYING = "FLYING"
    HOVERING = "HOVERING"
    LANDING = "LANDING"
    RETURNING_HOME = "RETURNING_HOME"
    EMERGENCY = "EMERGENCY"

class CommandType(Enum):
    """
    Represents the command types supported by the system.
    """

    TAKEOFF = "TAKEOFF"
    LAND = "LAND"
    GOTO = "GOTO"
    RETURN_HOME = "RETURN_HOME"
    HOVER = "HOVER"
    TELEMETRY = "TELEMETRY"
    UNKNOWN = "UNKNOWN"

class MissionStatus(Enum):
    """
    Represents the current status of a mission.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskStatus(Enum):
    """
    Represents the execution status of a task within a mission.
    """

    WAITING = "WAITING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"