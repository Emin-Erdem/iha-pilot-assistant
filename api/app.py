from fastapi import FastAPI, HTTPException

from api.schemas import MissionRequest
from api.services import ApiMissionService

from exceptions.drone_exception import DroneException


app = FastAPI(
    title="IHA Pilot Assistant API",
    description="API for the AI-assisted drone mission system.",
    version="0.2.0",
)

mission_service = ApiMissionService()


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Returns basic API status information.
    """

    return {
        "message": "IHA Pilot Assistant API is running."
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Returns the health status of the API.
    """

    return {
        "status": "healthy"
    }


@app.post("/missions/run")
def run_mission(request: MissionRequest) -> dict:
    """
    Runs a mission received through the API.
    """

    try:
        return mission_service.run_mission(request)

    except DroneException as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except KeyError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Missing command parameter: {error.args[0]}"
        ) from error


@app.get("/telemetry")
def get_telemetry() -> dict:
    """
    Returns the latest telemetry snapshot.
    """

    telemetry = mission_service.get_latest_telemetry()

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="No telemetry is available yet."
        )

    return telemetry


@app.get("/reports/latest")
def get_latest_report() -> dict:
    """
    Returns the latest flight report.
    """

    report = mission_service.get_latest_report()

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="No flight report is available yet."
        )

    return report