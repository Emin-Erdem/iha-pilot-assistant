from domain.drone import Drone
from domain.mission import Mission


class FlightReportService:
    """
    Creates a summary report after a mission is completed.
    """

    def create_report(self, mission: Mission, drone: Drone) -> dict:
        """
        Creates a flight report.
        """

        report = {
            "mission_name": mission.name,
            "commands_executed": drone.statistics.commands_executed,
            "distance_travelled": round(
                drone.statistics.distance_travelled,
                2
            ),
            "max_altitude": drone.statistics.max_altitude,
            "battery_used": drone.statistics.battery_used,
            "final_battery": drone.battery_level,
            "final_altitude": drone.altitude,
            "final_position": (
                drone.position.x,
                drone.position.y,
            ),
            "flight_mode": drone.mode.value,
        }

        return report