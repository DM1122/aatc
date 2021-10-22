# stdlib
import logging
import math

# external
import numpy as np
import pygame
from pygame.math import Vector2

LOG = logging.getLogger(__name__)


class Plane:
    def __init__(self, id, position, heading, channels):
        self.id = id
        self.color = (0, 255, 0)
        self.position = Vector2(position)
        self.speed = 0.140  # km/s
        self.heading = (
            heading  # degrees. zero is due north, positive angles counterclockwise.
        )
        self.status = "CRUISING"
        self.channels = channels
        self.transmit_frequency = 1  # Hz

        self.transmit = False

        self.shape = [Vector2(-0.1, 0), Vector2(0, 0.2), Vector2(0.1, 0)]
        self.transmit_time_prev = 0

        self.request_connection()

    def __str__(self):
        return f"Plane '{self.id}'\n\tPos: {self.position}\n\tHead: {self.heading}rad\n\tVel: {self.get_velocity()}"

    def get_velocity(self):
        return (
            Vector2(
                -1 * math.sin(math.radians(self.heading)),
                math.cos(math.radians(self.heading)),
            )
            * self.speed
        )

    def request_connection(self):
        LOG.info(f"Plane '{self.id}' requesting connection with ATC.")
        event_connection = pygame.event.Event(
            self.channels["CONNECTIONREQUEST"], plane_id=self.id
        )
        pygame.event.post(event_connection)

    def transmit_telemetry(self):
        transmit_event = pygame.event.Event(
            self.channels["TELEMETRY"],
            plane_id=self.id,
            telemetry={"position": self.position, "status": self.status},
        )
        LOG.debug(f"Plane '{self.id}' transmitting telemetry: {transmit_event}.")

        pygame.event.post(transmit_event)

    def receive_flight_plan(self, plan):
        return

    def navigate(self, position):
        self.heading = math.atan2(position.y, position.x)

    def hold(self, target):
        target_vector = position

    def update(self):
        time = pygame.time.get_ticks()
        if (
            self.transmit
            and time >= self.transmit_time_prev + (1 / self.transmit_frequency) * 1000
        ):
            self.transmit_telemetry()
            self.transmit_time_prev = time

    def hold(self):
        self.status = "HOLDING"

    def follow_plan():
        position_future

    def draw(self, surface, position, scale):
        shape_oriented = np.array(
            [point.rotate(-1 * self.heading + 180) for point in self.shape]
        )
        shape_scaled = shape_oriented * scale
        shape_translated = shape_scaled + position

        pygame.draw.polygon(
            surface=surface,
            color=self.color,
            points=shape_translated,
            width=1,
        )


class ATCZone:
    def __init__(self):
        self.color = (0, 255, 0)
        self.radius = 10

    def draw(self, surface, position, scale):
        pygame.draw.circle(
            surface=surface,
            color=self.color,
            center=position,
            radius=10 * scale,
            width=1,
        )


class Runway:
    def __init__(self, id, entry_coord, exit_coord):
        self.id = id
        self.entry_coord = entry_coord
        self.exit_coord = exit_coord
        self.color = (0, 255, 0)

    def draw(self, surface, position_start, position_end):
        pygame.draw.line(
            surface=surface,
            color=self.color,
            start_pos=position_start,
            end_pos=position_end,
            width=1,
        )


class Path:
    def __init__(self, waypoints, radius=0.1):
        self.waypoints = waypoints
        self.radius = radius
        self.color = (0, 0, 255)

    def draw(self, surface, waypoints_tranformed, scale):

        for i in range(len(waypoints_tranformed) - 1):
            # draw waypoint marker
            pygame.draw.circle(
                surface=surface,
                color=self.color,
                center=waypoints_tranformed[i],
                radius=self.radius * scale,
                width=1,
            )

            # draw path line
            pygame.draw.line(
                surface=surface,
                color=self.color,
                start_pos=waypoints_tranformed[i],
                end_pos=waypoints_tranformed[i + 1],
                width=1,
            )

        # draw last waypoint marker as a square
        marker_rect = pygame.Rect(
            (0, 0), (self.radius * 2 * scale, self.radius * 2 * scale)
        )
        marker_rect.center = waypoints_tranformed[-1]
        pygame.draw.rect(
            surface=surface,
            color=self.color,
            rect=marker_rect,
            width=1,
        )
