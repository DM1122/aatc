# stdlib
import logging
from collections import deque
from pprint import pformat

# external
import pygame
from game_objects import Path

LOG = logging.getLogger(__name__)


class AATC:
    def __init__(self, channels, runways):
        self.channels = channels
        self.planes = {}
        self.queue = deque()
        self.runways = self._build_strip_dict(runways)
        self.paths = []

        self.paths.append(Path(waypoints=[(0, 0), (0, 1), (0, 2)], radius=0.1))
        self.paths.append(Path(waypoints=[(10, -1), (6, 3), (-4, 1)], radius=0.1))
        self.paths.append(Path(waypoints=[(1, 1), (2, 2), (9, 2)], radius=0.1))

    def __str__(self):
        return f"AATC Info:\nActive connections:\t{len(self.planes)}\nPlanes:\n{pformat(self.planes)}\nQueue: {self.queue}"

    @staticmethod
    def _build_strip_dict(runways):
        strip_dict = {}
        for runway in runways:
            strip_dict[runway.id] = {
                "entry_coord": runway.entry_coord,
                "exit_coord": runway.exit_coord,
                "status": "OPEN",
            }
        return strip_dict

    def get_nearest_open_runway_to_plane(self, plane_id):
        plane_position = self.planes[plane_id]["position"]

        runways_open = [
            runway_id
            for runway_id in self.runways
            if self.runways[runway_id]["status"] == "OPEN"
        ]

        distances = {}
        for runway_open_id in runways_open:
            runway_position = self.runways[runway_open_id]["entry_coord"]
            distance = (plane_position - runway_position).length()
            distances[runway_open_id] = distance

        nearest_runway_id = min(distances, key=distances.get)

        return nearest_runway_id

    def add_plane(self, plane_id):
        LOG.info(
            f"Received connection request from plane '{plane_id}'. Adding to planes and queue."
        )
        self.planes[plane_id] = {"position": None, "status": None}
        self.queue.append(plane_id)
        event_connection_confirmation = pygame.event.Event(
            self.channels["CONNECTIONCONFIRMATION"], plane_id=plane_id
        )
        pygame.event.post(event_connection_confirmation)

    def update_telemetry(self, plane_id, telemetry):
        LOG.debug(f"Received telemetry from plane '{plane_id}'.")
        self.planes[plane_id]["position"] = telemetry["position"]
        self.planes[plane_id]["status"] = telemetry["status"]

    def generate_flight_plan(self, start, end, steps):
        plan = [start]

        plan.append(end)

        return plan

    def hold_plane(self, plane_id):
        LOG.info(f"Holding plane '{plane_id}'")
        event_hold = pygame.event.Event(self.channels["HOLD"], plane_id=plane_id)
        pygame.event.post(event_hold)

    def send_flight_plan(plane_id, plan):
        return
