from application.mission_service import MissionService

from domain.command import Command
from domain.enums import CommandType
from domain.mission import Mission

from api.schemas import MissionRequest


class ApiMissionService:
    """
    Converts API requests into domain missions and delegates
    mission execution to MissionService.
    """

    def __init__(self):
        self.mission_service = MissionService()

    def run_mission(self, request: MissionRequest) -> dict:
        """
        Converts a mission request into domain objects and runs it.
        """

        commands: list[Command] = []

        for command_request in request.commands:
            try:
                command_type = CommandType[
                    command_request.type.upper()
                ]

            except KeyError as error:
                raise ValueError(
                    f"Unsupported command type: "
                    f"{command_request.type}"
                ) from error

            commands.append(
                Command(
                    command_type=command_type,
                    parameters=command_request.parameters
                )
            )

        mission = Mission(
            name=request.name,
            commands=commands
        )

        return self.mission_service.run(mission)

    def get_latest_telemetry(self) -> dict | None:
        """
        Returns the latest telemetry snapshot.
        """

        return self.mission_service.get_latest_telemetry()

    def get_latest_report(self) -> dict | None:
        """
        Returns the most recently generated flight report.
        """

        return self.mission_service.get_latest_report()

    def reset(self) -> None:
        """
        Resets the drone and mission state.
        """

        self.mission_service.reset()