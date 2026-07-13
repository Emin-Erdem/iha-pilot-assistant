from exceptions.drone_exception import DroneException


class InvalidCommandException(DroneException):
    """
    Raised when an unsupported command is received.
    """
    pass