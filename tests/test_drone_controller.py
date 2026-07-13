import unittest

from application.drone_controller import DroneController
from domain.drone import Drone
from exceptions.altitude_limit_exception import AltitudeLimitException


class DroneControllerTest(unittest.TestCase):

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

    def test_return_home(self):
        self.controller.goto(150, 80)
        self.controller.return_home()
        self.assertEqual(self.drone.position.x, 0.0)
        self.assertEqual(self.drone.position.y, 0.0)

    def test_takeoff_above_max_altitude(self):
        with self.assertRaises(AltitudeLimitException):
            self.controller.takeoff(500)


if __name__ == "__main__":
    unittest.main()