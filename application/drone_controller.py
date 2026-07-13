from infrastructure.logger import Logger

from domain.drone import Drone
from domain.mission import Mission
from domain.command import Command
from domain.enums import CommandType, FlightMode


class DroneController:
    """
    Executes validated missions on the drone.
    """

    def __init__(self, drone: Drone):
        """
        Initializes the controller with a drone instance.
        """
        self.drone = drone
        self.logger = Logger()

    def execute_mission(self, mission: Mission) -> None:
        """
        Executes all commands in the mission sequentially.
        """
        for command in mission.commands:
            self.execute_command(command)

    def execute_command(self, command: Command) -> None:
        """
        Executes a single command.
        """

        if command.command_type == CommandType.TAKEOFF:

            self.takeoff(
                command.parameters["altitude"]
            )

        elif command.command_type == CommandType.LAND:

            self.land()

        elif command.command_type == CommandType.GOTO:

            self.goto(
                command.parameters["x"],
                command.parameters["y"]
            )

        elif command.command_type == CommandType.HOVER:

            self.hover(
                command.parameters["duration"]
            )

        elif command.command_type == CommandType.RETURN_HOME:

            self.return_home()

    def takeoff(self, altitude: float) -> None:
        """
        Takes off to the specified altitude.
        """

        self.drone.mode = FlightMode.TAKING_OFF
        self.drone.speed = 5.0
        self.drone.altitude = altitude
        self.drone.mode = FlightMode.FLYING

        self.update_battery(2.0)

        self.logger.info(f"Drone took off to {altitude} meters.")

    def land(self) -> None:
        """
        Lands the drone safely.
        """

        self.drone.mode = FlightMode.LANDING
        self.drone.speed = 0.0
        self.drone.altitude = 0.0
        self.drone.mode = FlightMode.IDLE

        self.update_battery(1.0)

        self.logger.info("Drone landed successfully.")

    def goto(self, x: float, y: float) -> None:
        """
        Moves the drone to the target position.
        """

        self.drone.mode = FlightMode.FLYING
        self.drone.speed = 10.0

        self.drone.position.x = x
        self.drone.position.y = y

        self.update_battery(3.0)

        self.logger.info(f"Drone moved to ({x}, {y}).")

    def hover(self, duration: int) -> None:
        """
        Keeps the drone hovering.
        """

        self.drone.mode = FlightMode.HOVERING
        self.drone.speed = 0.0

        self.update_battery(duration * 0.2)

        self.drone.mode = FlightMode.FLYING

        self.logger.info(f"Drone hovered for {duration} seconds.")

    def return_home(self) -> None:
        """
        Returns the drone to its home position.
        """

        self.drone.mode = FlightMode.RETURNING_HOME
        self.drone.speed = 10.0

        self.drone.position.x = self.drone.home_position.x
        self.drone.position.y = self.drone.home_position.y

        self.update_battery(3.0)

        self.drone.mode = FlightMode.FLYING

        self.logger.info("Drone returned to home position.")

    def update_battery(self, consumption: float) -> None:
        """
        Updates the battery level after an operation.
        """

        self.drone.battery_level -= consumption

        if self.drone.battery_level < 0:
            self.drone.battery_level = 0