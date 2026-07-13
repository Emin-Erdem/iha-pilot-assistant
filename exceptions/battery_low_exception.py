from exceptions.drone_exception import DroneException


class BatteryLowException(DroneException):
    """
    Raised when the battery is too low to execute a command.
    """
    pass