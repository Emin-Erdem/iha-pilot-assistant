from exceptions.drone_exception import DroneException


class AltitudeLimitException(DroneException):
    """
    Raised when altitude exceeds the configured limit.
    """
    pass