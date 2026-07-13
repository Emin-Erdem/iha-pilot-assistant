import unittest

from application.drone_controller import DroneController

from config.settings import Settings

from domain.drone import Drone

from exceptions.altitude_limit_exception import AltitudeLimitException
from exceptions.battery_low_exception import BatteryLowException


class DroneControllerTest(unittest.TestCase):
    """
    Tests the core behaviours and safety rules of DroneController.
    """

    def setUp(self):
        self.drone = Drone()
        self.controller = DroneController(self.drone)

    def test_takeoff_changes_altitude(self):
        self.controller.takeoff(20)

        self.assertEqual(self.drone.altitude, 20)

    def test_land_sets_altitude_to_zero(self):
        self.controller.takeoff(20)
        self.controller.land()

        self.assertEqual(self.drone.altitude, 0.0)

    def test_goto_changes_position(self):
        self.controller.goto(100, 50)

        self.assertEqual(self.drone.position.x, 100)
        self.assertEqual(self.drone.position.y, 50)

    def test_return_home_changes_position_to_home(self):
        self.controller.goto(150, 80)
        self.controller.return_home()

        self.assertEqual(
            self.drone.position.x,
            self.drone.home_position.x
        )
        self.assertEqual(
            self.drone.position.y,
            self.drone.home_position.y
        )

    def test_takeoff_above_max_altitude_raises_exception(self):
        with self.assertRaises(AltitudeLimitException):
            self.controller.takeoff(
                Settings.MAX_ALTITUDE + 1
            )

    def test_takeoff_with_low_battery_raises_exception(self):
        self.drone.battery_level = Settings.MIN_BATTERY - 1

        with self.assertRaises(BatteryLowException):
            self.controller.takeoff(20)

    def test_takeoff_updates_max_altitude_statistic(self):
        self.controller.takeoff(25)

        self.assertEqual(
            self.drone.statistics.max_altitude,
            25
        )

    def test_goto_updates_distance_statistic(self):
        self.controller.goto(3, 4)

        self.assertEqual(
            self.drone.statistics.distance_travelled,
            5.0
        )

    def test_command_execution_updates_command_count(self):
        from domain.command import Command
        from domain.enums import CommandType

        command = Command(
            command_type=CommandType.TAKEOFF,
            parameters={"altitude": 20}
        )

        self.controller.execute_command(command)

        self.assertEqual(
            self.drone.statistics.commands_executed,
            1
        )

    def test_battery_never_falls_below_zero(self):
        self.drone.battery_level = 1.0

        self.controller.update_battery(5.0)

        self.assertEqual(self.drone.battery_level, 0)


if __name__ == "__main__":
    unittest.main()