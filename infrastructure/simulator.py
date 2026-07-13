from application.mission_runner import MissionRunner

from exceptions.drone_exception import DroneException

from domain.drone import Drone
from domain.mission import Mission


class Simulator:
    """
    Runs missions inside the simulation and displays their results.
    """

    def __init__(self):
        self.drone = Drone()
        self.mission_runner = MissionRunner(self.drone)

    def run(self, mission: Mission) -> None:
        """
        Runs a mission and displays telemetry and report output.
        """

        print("========== Simulation Started ==========")

        try:
            report = self.mission_runner.run(mission)

            print("========== Simulation Finished ==========")

            self.print_telemetry()
            self.print_flight_report(report)

        except DroneException as error:
            print()
            print("========== Simulation Aborted ==========")
            print(f"ERROR: {error}")

    def print_telemetry(self) -> None:
        """
        Displays the latest telemetry snapshot.
        """

        telemetry = self.mission_runner.last_telemetry()

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

    def print_flight_report(self, report: dict) -> None:
        """
        Displays the final flight report.
        """

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
        print(f"Final Position     : {report['final_position']}")
        print(f"Flight Mode        : {report['flight_mode']}")