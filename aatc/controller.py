# stdlib
import logging
from collections import OrderedDict, deque

# external
import pygame

LOG = logging.getLogger(__name__)


class AATC:
    def __init__(self, channels):
        self.database = {}
        self.queue = deque()
        self.channels = channels

    def __str__(self):
        return f"AATC:\n\tActive connections:\t{len(self.database)}\n\tLedger:\t{self.database}"

    def receive_connection(self, plane_id):
        LOG.info(
            f"Received connection request from plane '{plane_id}'. Adding to database and queue."
        )
        self.database[plane_id] = {"position": None, "status": None}
        self.queue.append(plane_id)
        event_connection_confirmation = pygame.event.Event(
            self.channels["CONNECTIONCONFIRMATION"], plane_id=plane_id
        )
        pygame.event.post(event_connection_confirmation)

    def update_telemetry(self, plane_id, telemetry):
        LOG.debug(f"Received telemetry from plane '{plane_id}'.")
        self.database[plane_id]["position"] = telemetry["position"]

    def construct_flight_plan(self):
        return

    def send_flight_plan(plane_id, plan):
        return


# class Map:
#     def __init__(self):
#         self.map_radius = 10
#         self.strips = [
#             LandingStrip(id="A", start=(-0.5, -0.5), end=(-0.5, 0.5)),
#             LandingStrip(id="B", start=(0.5, -0.5), end=(0.5, 0.5)),
#         ]
