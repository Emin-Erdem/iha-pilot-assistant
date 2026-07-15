from time import sleep
from typing import Callable

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

    def __init__(
        self,
        drone: Drone,
        on_state_change: Callable[[], None] | None = None,
        movement_steps: int = 10,
        movement_step_delay: float = 0.0,
    ):
        self.drone = drone
        self.logger = Logger()

        self.on_state_change = on_state_change
        self.movement_steps = max(1, movement_steps)
        self.movement_step_delay = max(
            0.0,
            movement_step_delay
        )

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
                f"maximum allowed altitude "
                f"({Settings.MAX_ALTITUDE} m)."
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

        self._notify_state_change()

        self.logger.info(
            f"Drone took off to {altitude} meters."
        )

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

        self._notify_state_change()

        self.logger.info("Drone landed successfully.")

    def goto(self, x: float, y: float) -> None:
        """
        Moves the drone gradually to the target position.
        """

        self.drone.mode = FlightMode.FLYING
        self.drone.speed = Settings.CRUISE_SPEED

        self._move_to(
            target_x=x,
            target_y=y,
            flight_mode=FlightMode.FLYING,
        )

        self.update_battery(
            Settings.MOVE_BATTERY_USAGE
        )

        self._notify_state_change()

        self.logger.info(
            f"Drone moved to ({x}, {y})."
        )

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

        self._notify_state_change()

        self.drone.mode = FlightMode.FLYING

        self.logger.info(
            f"Drone hovered for {duration} seconds."
        )

    def return_home(self) -> None:
        """
        Returns the drone gradually to its home position.
        """

        self.drone.mode = FlightMode.RETURNING_HOME
        self.drone.speed = Settings.CRUISE_SPEED

        self._move_to(
            target_x=self.drone.home_position.x,
            target_y=self.drone.home_position.y,
            flight_mode=FlightMode.RETURNING_HOME,
        )

        self.update_battery(
            Settings.MOVE_BATTERY_USAGE
        )

        self.drone.mode = FlightMode.FLYING

        self._notify_state_change()

        self.logger.info(
            "Drone returned to home position."
        )

    def _move_to(
        self,
        target_x: float,
        target_y: float,
        flight_mode: FlightMode,
    ) -> None:
        """
        Moves the drone to a destination using small steps.
        """

        start_x = self.drone.position.x
        start_y = self.drone.position.y

        delta_x = target_x - start_x
        delta_y = target_y - start_y

        total_distance = (
            delta_x ** 2 +
            delta_y ** 2
        ) ** 0.5

        self.drone.mode = flight_mode

        for step in range(1, self.movement_steps + 1):
            progress = step / self.movement_steps

            self.drone.position.x = (
                start_x + delta_x * progress
            )

            self.drone.position.y = (
                start_y + delta_y * progress
            )

            self._notify_state_change()

            if self.movement_step_delay > 0:
                sleep(self.movement_step_delay)

        self.drone.statistics.distance_travelled += (
            total_distance
        )

    def _notify_state_change(self) -> None:
        """
        Notifies the caller after the drone state changes.
        """

        if self.on_state_change is not None:
            self.on_state_change()

    def update_battery(self, consumption: float) -> None:
        """
        Updates the battery level after an operation.
        """

        actual_consumption = min(
            consumption,
            self.drone.battery_level
        )

        self.drone.statistics.battery_used += (
            actual_consumption
        )

        self.drone.battery_level -= actual_consumption

        if self.drone.battery_level < 0:
            self.drone.battery_level = 0