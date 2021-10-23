"""Module for AATC."""
# stdlib
import logging
from collections import deque
from pprint import pformat

# external
import pygame

LOG = logging.getLogger(__name__)


class AATC:
    """The automated air traffic controller. Responsible for managing air space traffic.

    Args:
        channels (dict): Dictionary of pygame event channels to be used to communicate
            with the planes.
        runways (list): List of runway game objects present in the simulation.
    """

    def __init__(self, channels, runways):
        self.channels = channels
        self.planes = {}
        self.queue = deque()  # plane queue
        self.runways = self._build_runway_dict(runways)
        self.paths = []  # list of active paths

    def __str__(self):
        return f"""AATC Info:\nActive connections:\t{len(self.planes)}\nPlanes:\n
        {pformat(self.planes)}\nQueue: {self.queue}"""

    @staticmethod
    def _build_runway_dict(runways):
        """Builds a dictionary of runways from their gameobject information."""
        strip_dict = {}
        for runway in runways:
            strip_dict[runway.id] = {
                "entry_coord": runway.entry_coord,
                "exit_coord": runway.exit_coord,
                "status": "OPEN",
            }
        return strip_dict

    def get_nearest_open_runway_to_plane(self, plane_id):
        """Retrieves the nearest open runway to the plane.

        Args:
            plane_id (str): ID of the plane of interest.

        Returns:
            str: ID of nearest open runway.
        """
        plane_position = self.planes[plane_id]["position"]

        runways_open = [
            runway_id
            for runway_id in self.runways
            if self.runways[runway_id]["status"] == "OPEN"
        ]  # TODO: use .items()

        distances = {}
        for runway_open_id in runways_open:
            runway_position = self.runways[runway_open_id]["entry_coord"]
            distance = (plane_position - runway_position).length()
            distances[runway_open_id] = distance

        nearest_runway_id = min(distances, key=distances.get)

        return nearest_runway_id

    def add_plane(self, plane_id):
        """Add a plane to the ATC database of planes and insert to the landing queue.

        Args:
            plane_id (str): ID of the plane to be added.
        """
        LOG.info(
            f"Received connection request from plane '{plane_id}'. "
            "Adding to planes and queue."
        )
        self.planes[plane_id] = {"position": None, "status": None}
        self.queue.append(plane_id)
        event_connection_confirmation = pygame.event.Event(
            self.channels["CONNECTIONCONFIRMATION"], plane_id=plane_id
        )
        pygame.event.post(event_connection_confirmation)

    def update_telemetry(self, plane_id, telemetry):
        """Update the telemetry of a plane in the database from new data.

        Args:
            plane_id (str): ID of the plane to be updated.
            telemetry (dict): Dictionary of telemetry data.
        """
        LOG.debug(f"Received telemetry from plane '{plane_id}'.")
        self.planes[plane_id]["position"] = telemetry["position"]
        self.planes[plane_id]["status"] = telemetry["status"]

    def generate_flight_plan(self, start, end, steps):
        raise NotImplementedError()

    def hold_plane(self, plane_id):
        """Instruct a plane to hold at its currnent position.

        Args:
            plane_id (str): ID of the plane to be held.
        """
        LOG.info(f"Holding plane '{plane_id}'")
        event_hold = pygame.event.Event(self.channels["HOLD"], plane_id=plane_id)
        pygame.event.post(event_hold)

    def send_flight_plan(self, plane_id, plan):
        raise NotImplementedError()
