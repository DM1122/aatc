# stdlib
import logging
import math

# external
import numpy as np
import pygame
from pygame.math import Vector2

LOG = logging.getLogger(__name__)


class GameEngine:
    def __init__(self, screen_size=(500, 500)):
        # region game config
        # screen
        self.screen_fps = 60
        self.screen_color = (0, 0, 0)
        self.screen_scale = 25  # pixels per km
        self.screen_size = Vector2(screen_size)

        # UI
        self.UI_draw_plane_keepout = False

        # world
        self.origin = self.screen_size // 2

        # planes
        self.plane_spawn_rate = 15  # avg sec per plane
        # endregion

        # region events
        self.SPAWNPLANEEVENT = pygame.USEREVENT + 1
        # endregion

        # region setup
        self.RNG = np.random.default_rng()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("AATC - David Maranto 2021")

        # instantiating game objects
        self.atc_zone = ATCZone()

        self.planes = []

        self.strips = [
            Strip(id=0, start_coord=Vector2(-0.5, -0.5), end_coord=Vector2(-0.5, 0.5)),
            Strip(id=1, start_coord=Vector2(0.5, -0.5), end_coord=Vector2(0.5, 0.5)),
        ]

        # endregion

    def spawn_plane(self):
        id = len(self.planes)
        spawn_angle = self.RNG.random(1) * 2 * math.pi  # random angle in radians
        spawn_position = (
            Vector2(math.cos(spawn_angle), math.sin(spawn_angle)) * self.atc_zone.radius
        )
        spawn_heading = math.atan2(-1 * spawn_position.y, -1 * spawn_position.x)
        self.planes.append(Plane(id=id, position=spawn_position, heading=spawn_heading))

        LOG.info(f"Spawning plane '{id}' at {spawn_position}")

    def start_plane_spawn_timer(self):
        spawn_interval = round(
            np.clip(
                a=self.RNG.normal(loc=self.plane_spawn_rate, scale=2.0),
                a_min=1,
                a_max=30,
            )
        )
        pygame.time.set_timer(event=self.SPAWNPLANEEVENT, millis=spawn_interval * 1000)
        LOG.info(f"Spawning next plane in {spawn_interval}s")

    def vector_to_screen(self, vector):
        """Transforms a vector in game coordinates to screen coordinates.

        Args:
            vector (list-like): Some 2D vector in game coordinates.

        Returns:
            pygame.math.Vector2D: The vector represented in screen coordinates.
        """
        v = Vector2(vector) if type(vector) is not Vector2 else vector
        v = Vector2(v.x * -1, v.y)
        v_screen = self.origin - v

        return v_screen

    def update(self):
        # physics update

        for plane in self.planes:
            plane.position += plane.get_velocity() * (self.clock.get_time() * 10 ** -3)

        pass

    def draw(self):
        self.screen.fill(self.screen_color)

        self.atc_zone.draw(
            surface=self.screen,
            position=self.vector_to_screen((0, 0)),
            scale=self.screen_scale,
        )

        for plane in self.planes:
            plane.draw(
                surface=self.screen,
                position_screen=self.vector_to_screen(plane.position),
                scale=self.screen_scale,
            )
            # LOG.info(f"Plane screen pos: {self.vector_to_screen(plane.position)}")

        for strip in self.strips:
            strip.draw(
                surface=self.screen,
                translate_func=self.vector_to_screen,
                scale=self.screen_scale,
            )

        pygame.display.flip()
        self.clock.tick(self.screen_fps)


class Plane:
    def __init__(self, id, position, heading):
        self.id = id
        self.color = (0, 255, 0)
        self.position = Vector2(position)
        self.speed = 0.140  # km/s
        self.heading = (
            heading  # radians. zero is due north, positive angles counterclockwise.
        )

        self.shape = [Vector2(-0.1, 0), Vector2(0, 0.2), Vector2(0.1, 0)]

    def __str__(self):
        return f"Plane '{self.id}'\n\tPos: {self.position}\n\tHead: {self.heading}rad\n\tVel: {self.get_velocity()}"

    def get_velocity(self):
        return Vector2(math.cos(self.heading), math.sin(self.heading)) * self.speed

    def draw(self, surface, position_screen, scale):
        shape_oriented = [
            vertex.rotate(math.degrees(self.heading) - 90) for vertex in self.shape
        ]

        pygame.draw.polygon(
            surface=surface,
            color=self.color,
            points=((np.array(shape_oriented) + self.position) * scale)
            + position_screen,
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


class Strip:
    def __init__(self, id, start_coord, end_coord):
        self.id = id
        self.start_coord = start_coord
        self.end_coord = end_coord
        self.color = (0, 255, 0)

    def draw(self, surface, translate_func, scale):
        pygame.draw.line(
            surface=surface,
            color=self.color,
            start_pos=translate_func(self.start_coord * scale),
            end_pos=translate_func(self.end_coord * scale),
            width=1,
        )
