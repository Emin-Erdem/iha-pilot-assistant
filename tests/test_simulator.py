from application.mission_loader import MissionLoader
from infrastructure.simulator import Simulator


loader = MissionLoader()

mission = loader.load("missions/demo_mission.json")

simulator = Simulator()

simulator.run(mission)