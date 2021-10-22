# stdlib
import logging
import math
import random
import string
from pathlib import Path

# external
import controller
import numpy as np
import pygame
from game_objects import ATCZone, Plane, Runway
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
        self.paused = False

        # assets
        self.audio_volume = 0.1
        self.assets_audio_path = Path("aatc/assets/audio")
        self.user_interact_audio = Path("user_interact.wav")
        self.plane_spawn_audio = Path("plane_spawn.wav")
        self.plane_land_audio = Path("plane_land.wav")
        self.plane_crash_audio = Path("plane_crash.wav")

        self.plane_protected_radius = 0.1  # km

        # UI
        self.draw_gizmos = True

        # world
        self.origin = self.screen_size // 2

        # planes
        self.spawn_planes = True
        self.spawn_planes_interval = 0
        self.spawn_planes_interval_avg = 15  # avg sec per plane
        self.spawn_planes_interval_max = 30  # sec
        self.spawn_planes_interval_min = 1  # sec
        self.spawn_planes_time_prev = 0  # msec

        # endregion

        # events
        self.events = {
            "CONNECTIONREQUEST": pygame.event.custom_type(),
            "CONNECTIONCONFIRMATION": pygame.event.custom_type(),
            "TELEMETRY": pygame.event.custom_type(),
            "FLIGHTPLAN": pygame.event.custom_type(),
            "HOLD": pygame.event.custom_type(),
        }

        # region setup
        self.RNG = np.random.default_rng()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("AATC - David Maranto 2021")

        self.planes = []

        self.runways = [
            Runway(
                id=0, entry_coord=Vector2(-0.5, -0.5), exit_coord=Vector2(-0.5, 0.5)
            ),
            Runway(id=1, entry_coord=Vector2(0.5, -0.5), exit_coord=Vector2(0.5, 0.5)),
        ]

        # instantiating game objects
        self.atc_zone = ATCZone()
        self.atc = controller.AATC(channels=self.events, runways=self.runways)

        # endregion

    def spawn_plane(self):
        id = self.generate_id()
        spawn_angle = self.RNG.random(1) * 2 * math.pi  # random angle in radians
        spawn_position = (
            Vector2(math.cos(spawn_angle), math.sin(spawn_angle)) * self.atc_zone.radius
        )
        spawn_heading = math.degrees(
            math.pi - math.atan2(spawn_position.x, spawn_position.y)
        )
        LOG.info(
            f"Spawning plane '{id}' at {spawn_position} with heading {round(spawn_heading)}°"
        )
        self.planes.append(
            Plane(
                id=id,
                position=spawn_position,
                heading=spawn_heading,
                channels=self.events,
            )
        )

        self.play_audio(self.plane_spawn_audio)

    def vector_to_screen(self, vector):
        """Transforms a vector in game coordinates to screen coordinates.

        Args:
            vector (list-like): Some 2D vector in game coordinates.

        Returns:
            pygame.math.Vector2D: The vector represented in screen coordinates.
        """
        v = Vector2(vector) if type(vector) is not Vector2 else vector
        v = Vector2(v.x * -1, v.y) * self.screen_scale
        v_screen = self.origin - v

        return v_screen

    def play_audio(self, audio):
        sound = pygame.mixer.Sound(str(self.assets_audio_path / audio))
        sound.set_volume(self.audio_volume)
        sound.play()

    def update(self):
        time = pygame.time.get_ticks()

        # spawn plane
        if (
            self.spawn_planes == True
            and time >= self.spawn_planes_time_prev + self.spawn_planes_interval * 1000
        ):
            self.spawn_plane()
            self.spawn_planes_time_prev = time

            self.spawn_planes_interval = round(
                np.clip(
                    a=self.RNG.normal(loc=self.spawn_planes_interval_avg, scale=2.0),
                    a_min=self.spawn_planes_interval_min,
                    a_max=self.spawn_planes_interval_max,
                )
            )
            LOG.debug(f"Spawning next plane in {self.spawn_planes_interval}s")

        for plane in self.planes:
            plane.position += plane.get_velocity() * (self.clock.get_time() * 10 ** -3)
            plane.update()

        # self.atc.update()

    @staticmethod
    def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))

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
                position=self.vector_to_screen(plane.position),
                scale=self.screen_scale,
            )
            if self.draw_gizmos:
                LOG.debug(f"plane pos: {plane.position}")
                LOG.debug(f"screen pos {self.vector_to_screen(plane.position)}")
                pygame.draw.circle(
                    surface=self.screen,
                    color=(0, 0, 255),
                    center=self.vector_to_screen(plane.position),
                    radius=self.plane_protected_radius * self.screen_scale,
                    width=1,
                )

        for runway in self.runways:
            runway.draw(
                surface=self.screen,
                position_start=self.vector_to_screen(runway.entry_coord),
                position_end=self.vector_to_screen(runway.exit_coord),
            )

        if self.draw_gizmos:
            # draw path gizmos
            for path in self.atc.paths:
                waypoints_tranformed = [
                    self.vector_to_screen(waypoint) for waypoint in path.waypoints
                ]
                path.draw(
                    surface=self.screen,
                    waypoints_tranformed=waypoints_tranformed,
                    scale=self.screen_scale,
                )

        pygame.display.flip()
        self.clock.tick(self.screen_fps)
