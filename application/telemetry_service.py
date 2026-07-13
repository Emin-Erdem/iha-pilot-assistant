from domain.drone import Drone
from domain.telemetry import Telemetry

class TelemetryService:
    """
    Creates telemetry snapshots from the current drone state.
    """

    def __init__(self, drone: Drone):

        self.drone = drone


    def create_snapshot(self) -> Telemetry:
        """
        Creates a telemetry snapshot from the drone state.
        """

        return Telemetry(

            position=self.drone.position,

            altitude=self.drone.altitude,

            battery_level=self.drone.battery_level,

            speed=self.drone.speed,

            mode=self.drone.mode

        )