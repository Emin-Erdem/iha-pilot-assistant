from application.drone_controller import DroneController
from application.telemetry_service import TelemetryService
from application.telemetry_history import TelemetryHistory
from application.flight_report_service import FlightReportService

from infrastructure.mission_recorder import MissionRecorder

from exceptions.drone_exception import DroneException

from domain.drone import Drone
from domain.mission import Mission


class Simulator:
    """
    Runs drone missions inside the simulation.
    """

    def __init__(self):

        self.drone = Drone()

        self.controller = DroneController(self.drone)

        self.telemetry_service = TelemetryService(self.drone)

        self.telemetry_history = TelemetryHistory()

        self.flight_report_service = FlightReportService()

        self.mission_recorder = MissionRecorder()

    def run(self, mission: Mission):

        print("========== Simulation Started ==========")

        try:

            self.controller.execute_mission(mission)

            telemetry = self.telemetry_service.create_snapshot()

            self.telemetry_history.add(telemetry)

            print("========== Simulation Finished ==========")

            self.print_telemetry()

            report = self.print_flight_report(mission)

            self.mission_recorder.save(
                report,
                "reports/mission_report.json"
            )

        except DroneException as error:

            print()

            print("========== Simulation Aborted ==========")

            print(f"ERROR: {error}")

    def print_telemetry(self):

        telemetry = self.telemetry_history.last()

        if telemetry is None:
            return

        print()

        print("Telemetry")

        print("------------------------")

        print(f"Position : ({telemetry.position.x}, {telemetry.position.y})")

        print(f"Altitude : {telemetry.altitude} m")

        print(f"Battery  : {telemetry.battery_level}%")

        print(f"Speed    : {telemetry.speed} m/s")

        print(f"Mode     : {telemetry.mode.value}")

        print(f"Time     : {telemetry.timestamp}")

    def print_flight_report(self, mission: Mission) -> dict:

        report = self.flight_report_service.create_report(
            mission,
            self.drone
        )

        print()

        print("Flight Report")

        print("------------------------")

        print(f"Mission Name       : {report['mission_name']}")

        print(f"Commands Executed  : {report['commands_executed']}")

        print(f"Distance Travelled : {report['distance_travelled']} m")

        print(f"Max Altitude       : {report['max_altitude']} m")

        print(f"Battery Used       : {report['battery_used']}%")

        print(f"Final Battery      : {report['final_battery']}%")

        print(f"Final Altitude     : {report['final_altitude']} m")

        print(
            f"Final Position     : "
            f"{report['final_position']}"
        )

        print(f"Flight Mode        : {report['flight_mode']}")

        return report