from config.settings import Settings

from infrastructure.logger import Logger

from exceptions.battery_low_exception import BatteryLowException
from exceptions.altitude_limit_exception import AltitudeLimitException
from exceptions.invalid_command_exception import InvalidCommandException

from domain.drone import Drone
from domain.mission import Mission
from domain.command import Command
from domain.enums import CommandType, FlightMode


class DroneController:
    """
    Executes validated missions on the drone.
    """

    def __init__(self, drone: Drone):
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

        else:

            raise InvalidCommandException(
                f"Unsupported command: {command.command_type}"
            )

        self.drone.statistics.commands_executed += 1

    def takeoff(self, altitude: float) -> None:
        """
        Takes off to the specified altitude.
        """

        if self.drone.battery_level < Settings.MIN_BATTERY:
            raise BatteryLowException(
                f"Battery too low ({self.drone.battery_level}%). "
                f"Minimum required: {Settings.MIN_BATTERY}%."
            )

        if altitude > Settings.MAX_ALTITUDE:
            raise AltitudeLimitException(
                f"Requested altitude ({altitude} m) exceeds "
                f"maximum allowed altitude ({Settings.MAX_ALTITUDE} m)."
            )

        self.drone.mode = FlightMode.TAKING_OFF
        self.drone.speed = Settings.TAKEOFF_SPEED
        self.drone.altitude = altitude

        self.drone.statistics.max_altitude = max(
            self.drone.statistics.max_altitude,
            altitude
        )

        self.drone.mode = FlightMode.FLYING

        self.update_battery(
            Settings.TAKEOFF_BATTERY_USAGE
        )

        self.logger.info(f"Drone took off to {altitude} meters.")

    def land(self) -> None:
        """
        Lands the drone safely.
        """

        self.drone.mode = FlightMode.LANDING
        self.drone.speed = Settings.HOVER_SPEED
        self.drone.altitude = 0.0
        self.drone.mode = FlightMode.IDLE

        self.update_battery(
            Settings.LAND_BATTERY_USAGE
        )

        self.logger.info("Drone landed successfully.")

    def goto(self, x: float, y: float) -> None:
        """
        Moves the drone to the target position.
        """

        self.drone.mode = FlightMode.FLYING
        self.drone.speed = Settings.CRUISE_SPEED

        old_x = self.drone.position.x
        old_y = self.drone.position.y

        self.drone.position.x = x
        self.drone.position.y = y

        distance = (
            ((x - old_x) ** 2 + (y - old_y) ** 2)
        ) ** 0.5

        self.drone.statistics.distance_travelled += distance

        self.update_battery(
            Settings.MOVE_BATTERY_USAGE
        )

        self.logger.info(f"Drone moved to ({x}, {y}).")

    def hover(self, duration: int) -> None:
        """
        Keeps the drone hovering.
        """

        self.drone.mode = FlightMode.HOVERING
        self.drone.speed = Settings.HOVER_SPEED

        self.update_battery(
            duration *
            Settings.HOVER_BATTERY_PER_SECOND
        )

        self.drone.mode = FlightMode.FLYING

        self.logger.info(f"Drone hovered for {duration} seconds.")

    def return_home(self) -> None:
        """
        Returns the drone to its home position.
        """

        self.drone.mode = FlightMode.RETURNING_HOME
        self.drone.speed = Settings.CRUISE_SPEED

        old_x = self.drone.position.x
        old_y = self.drone.position.y

        self.drone.position.x = self.drone.home_position.x
        self.drone.position.y = self.drone.home_position.y

        distance = (
            (
                (self.drone.home_position.x - old_x) ** 2 +
                (self.drone.home_position.y - old_y) ** 2
            )
        ) ** 0.5

        self.drone.statistics.distance_travelled += distance

        self.update_battery(
            Settings.MOVE_BATTERY_USAGE
        )

        self.drone.mode = FlightMode.FLYING

        self.logger.info("Drone returned to home position.")

    def update_battery(self, consumption: float) -> None:
        """
        Updates the battery level after an operation.
        """

        self.drone.statistics.battery_used += consumption

        self.drone.battery_level -= consumption

        if self.drone.battery_level < 0:
            self.drone.battery_level = 0