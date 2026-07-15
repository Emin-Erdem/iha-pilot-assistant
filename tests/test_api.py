from fastapi.testclient import TestClient

from api.app import app, mission_service


client = TestClient(app)


def reset_mission_service() -> None:
    """
    Resets the shared API mission state before a test.
    """

    mission_service.reset()


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "IHA Pilot Assistant API is running."
    }


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_telemetry_returns_404_before_mission() -> None:
    reset_mission_service()

    response = client.get("/telemetry")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No telemetry is available yet."
    )


def test_latest_report_returns_404_before_mission() -> None:
    reset_mission_service()

    response = client.get("/reports/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No flight report is available yet."
    )


def test_run_mission_returns_flight_report() -> None:
    reset_mission_service()

    mission_payload = {
        "name": "API Test Mission",
        "commands": [
            {
                "type": "TAKEOFF",
                "parameters": {
                    "altitude": 20
                }
            },
            {
                "type": "GOTO",
                "parameters": {
                    "x": 100,
                    "y": 50
                }
            },
            {
                "type": "HOVER",
                "parameters": {
                    "duration": 5
                }
            },
            {
                "type": "RETURN_HOME",
                "parameters": {}
            },
            {
                "type": "LAND",
                "parameters": {}
            }
        ]
    }

    response = client.post(
        "/missions/run",
        json=mission_payload
    )

    assert response.status_code == 200

    report = response.json()

    assert report["mission_name"] == "API Test Mission"
    assert report["commands_executed"] == 5
    assert report["max_altitude"] == 20
    assert report["final_battery"] == 90.0
    assert report["final_position"] == [0.0, 0.0]
    assert report["flight_mode"] == "IDLE"


def test_telemetry_returns_data_after_mission() -> None:
    response = client.get("/telemetry")

    assert response.status_code == 200

    telemetry = response.json()

    assert telemetry["position"] == {
        "x": 0.0,
        "y": 0.0
    }
    assert telemetry["altitude"] == 0.0
    assert telemetry["battery_level"] == 90.0
    assert telemetry["mode"] == "IDLE"


def test_latest_report_returns_data_after_mission() -> None:
    response = client.get("/reports/latest")

    assert response.status_code == 200

    report = response.json()

    assert report["mission_name"] == "API Test Mission"
    assert report["commands_executed"] == 5


def test_invalid_command_returns_400() -> None:
    reset_mission_service()

    mission_payload = {
        "name": "Invalid Command Mission",
        "commands": [
            {
                "type": "FLY_TO_MARS",
                "parameters": {}
            }
        ]
    }

    response = client.post(
        "/missions/run",
        json=mission_payload
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported command type: FLY_TO_MARS"
    )


def test_altitude_limit_returns_400() -> None:
    reset_mission_service()

    mission_payload = {
        "name": "Unsafe Altitude Mission",
        "commands": [
            {
                "type": "TAKEOFF",
                "parameters": {
                    "altitude": 500
                }
            }
        ]
    }

    response = client.post(
        "/missions/run",
        json=mission_payload
    )

    assert response.status_code == 400
    assert "exceeds maximum allowed altitude" in (
        response.json()["detail"]
    )


def test_missing_command_parameter_returns_422() -> None:
    reset_mission_service()

    mission_payload = {
        "name": "Missing Parameter Mission",
        "commands": [
            {
                "type": "TAKEOFF",
                "parameters": {}
            }
        ]
    }

    response = client.post(
        "/missions/run",
        json=mission_payload
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Missing command parameter: altitude"
    )