from time import sleep

from application.drone_controller import DroneController
from application.telemetry_service import TelemetryService
from application.telemetry_history import TelemetryHistory
from application.flight_report_service import FlightReportService

from infrastructure.mission_recorder import MissionRecorder

from domain.drone import Drone
from domain.mission import Mission


class MissionRunner:
    """
    Executes a complete mission workflow.
    """

    def __init__(self, drone: Drone):
        self.drone = drone
        self.controller = DroneController(drone)
        self.telemetry_service = TelemetryService(drone)
        self.telemetry_history = TelemetryHistory()
        self.flight_report_service = FlightReportService()
        self.mission_recorder = MissionRecorder()

    def run(
        self,
        mission: Mission,
        command_delay: float = 0.0
    ) -> dict:
        """
        Runs every mission command and records telemetry
        after each command.

        command_delay defines how many seconds to wait
        between commands.
        """

        self.telemetry_history.clear()

        for index, command in enumerate(mission.commands):
            self.controller.execute_command(command)

            telemetry = self.telemetry_service.create_snapshot()

            self.telemetry_history.add(telemetry)

            is_last_command = (
                index == len(mission.commands) - 1
            )

            if command_delay > 0 and not is_last_command:
                sleep(command_delay)

        report = self.flight_report_service.create_report(
            mission,
            self.drone
        )

        self.mission_recorder.save(
            report,
            "reports/mission_report.json"
        )

        return report

    def last_telemetry(self):
        """
        Returns the latest telemetry snapshot.
        """

        return self.telemetry_history.last()

    def get_telemetry_history(self):
        """
        Returns all telemetry snapshots from the latest mission.
        """

        return self.telemetry_history.get_all()