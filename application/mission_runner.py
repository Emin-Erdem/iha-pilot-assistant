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

    def run(self, mission: Mission) -> dict:
        """
        Runs a mission and returns the final report.
        """

        self.controller.execute_mission(mission)

        telemetry = self.telemetry_service.create_snapshot()
        self.telemetry_history.add(telemetry)

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