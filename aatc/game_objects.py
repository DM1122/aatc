"""An assortment of game object classes."""
# stdlib
import logging
import math

# external
import numpy as np
import pygame
from pygame.math import Vector2

LOG = logging.getLogger(__name__)


class Plane:
    """The plane game object. Handles flight, telemetry, and path-following logic.

    Args:
        plane_id (str): Unique ID to assign the plane.
        position (pygame.Vector2): Initial position.
        heading (num): Initial heading in degrees. From 0 to 360, where 0 is due north,
            increasing counterclockwise.
        channels (dict): Dictionary of pygame channel event codes.
    """

    def __init__(self, plane_id, position, heading, channels):
        # region config
        self.id = plane_id
        self.color = (0, 255, 0)
        self.position = Vector2(position)
        self.speed = 0.140  # km/s
        self.turn_rate = 0.1  # °/s
        self.heading = heading
        self.status = (
            "CRUISING"  # one of "CRUISING", "NAVIGATING", "HOLDING", "LANDING"
        )
        self.channels = channels
        self.transmit_frequency = 10  # Hz
        self.transmit = False
        self.shape = [Vector2(-0.1, 0), Vector2(0, 0.2), Vector2(0.1, 0)]
        self._transmit_time_prev = 0
        # endregion

        self.request_connection()

    def __str__(self):
        return f"""Plane '{self.id}'\n\tPos: {self.position}\n\tHead: {self.heading}rad
        \n\tVel: {self.get_velocity()}"""

    def get_velocity(self):
        """Calculate the velocity of the plane.

        Returns:
            pygame.Vector2: Plane's velocity vector.
        """
        return (
            Vector2(
                -1 * math.sin(math.radians(self.heading)),
                math.cos(math.radians(self.heading)),
            )
            * self.speed
        )

    def request_connection(self):
        """Send connection event to ATC with plane's ID."""
        LOG.info(f"Plane '{self.id}' requesting connection with ATC.")
        event_connection = pygame.event.Event(
            self.channels["CONNECTIONREQUEST"], plane_id=self.id
        )
        pygame.event.post(event_connection)

    def transmit_telemetry(self):
        """Post plane telemetry to telemetry channel."""
        transmit_event = pygame.event.Event(
            self.channels["TELEMETRY"],
            plane_id=self.id,
            telemetry={"position": self.position, "status": self.status},
        )
        LOG.debug(f"Plane '{self.id}' transmitting telemetry: {transmit_event}.")

        pygame.event.post(transmit_event)

    def receive_flight_plan(self, plan):
        raise NotImplementedError()

    def navigate(self):
        raise NotImplementedError()

    def hold(self):
        raise NotImplementedError()

    def update(self):
        """Schedule and execute telemtry updates."""
        time = pygame.time.get_ticks()
        if (
            self.transmit
            and time >= self._transmit_time_prev + (1 / self.transmit_frequency) * 1000
        ):
            self.transmit_telemetry()
            self._transmit_time_prev = time

    def follow_plan(self):
        raise NotImplementedError()

    def draw(self, surface, position, scale):
        """Render plane game object on screen.

        Args:
            surface (pygame.Surface): The pygame window on which to render the plane.
            position (Vector2): Plane position in screen coordinates.
            scale (num): screen scale factor.
        """
        shape_oriented = np.array(
            [point.rotate(-1 * self.heading + 180) for point in self.shape]
        )  # rotate plane shape to heading
        shape_scaled = shape_oriented * scale
        shape_translated = shape_scaled + position

        pygame.draw.polygon(
            surface=surface,
            color=self.color,
            points=shape_translated,
            width=1,
        )


class Runway:
    """The runway game object.

    Args:
        runway_id (str): Unique ID to assign the runway.
        entry_coord (pygame.Vector2): Entry coordinate.
        exit_coord (pygame.Vector2): Exit coordinate.
    """

    def __init__(self, runway_id, entry_coord, exit_coord):
        self.id = runway_id
        self.entry_coord = entry_coord
        self.exit_coord = exit_coord
        self.color = (0, 255, 0)

    def draw(self, surface, position_start, position_end):
        """Render runway game object on screen.

        Args:
            surface (pygame.surface): Pygame window on which to render runway.
            position_start (pygame.Vector2): Entry coordinate in screen coordinates.
            position_end (pygame.Vector2): Exit coordinate in screen coordinates.
        """
        pygame.draw.line(
            surface=surface,
            color=self.color,
            start_pos=position_start,
            end_pos=position_end,
            width=1,
        )


class ATCZone:
    """The air traffic control zone ring game object."""

    def __init__(self):
        self.color = (0, 255, 0)
        self.radius = 10

    def draw(self, surface, position, scale):
        """Render ATC zone game object on screen.

        Args:
            surface (pygame.surface): Pygame window on which to render ATC zone.
            position (pygame.Vector2): ATC zone center position in screen coordinates.
            scale (num): Screen scale.
        """
        pygame.draw.circle(
            surface=surface,
            color=self.color,
            center=position,
            radius=10 * scale,
            width=1,
        )


class Path:
    """The Path object is a convenience class for keeping track of a series of
        waypoints.

    Args:
        waypoints (list(pygame.Vector2)): List of waypoints coordinates which comprise
            the path, in order.
        radius (float, optional): Radius around which planes may be considered to be on
            the path for path-following purposes. Defaults to 0.1.
    """

    def __init__(self, waypoints, radius=0.1):

        self.waypoints = waypoints
        self.radius = radius
        self.color = (0, 0, 255)

    def draw(self, surface, waypoints_tranformed, scale):
        """Render path game object on screen.

        Args:
            surface (pygame.Surface): The surface on which to render the path.
            waypoints_tranformed (list(pygame.Vector2)): List of waypoints transformed
                to screen coordinates.
            scale (num): Screen scale factor.
        """

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
