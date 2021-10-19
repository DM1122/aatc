# stdlib
import logging
import math

# external
import numpy as np
import pygame
from pygame.math import Vector2
from pathlib import Path

LOG = logging.getLogger(__name__)


class GameEngine:
    def __init__(self, screen_size=(500, 500)):
        # region game config
        # screen
        self.screen_fps = 60
        self.screen_color = (0, 0, 0)
        self.screen_scale = 25  # pixels per km
        self.screen_size = Vector2(screen_size)

        # assets
        self.audio_volume = 0.1
        self.assets_audio_path = Path("aatc/assets/audio")
        self.user_interact_audio = Path("user_interact.wav")
        self.plane_spawn_audio = Path("plane_spawn.wav")
        self.plane_land_audio = Path("plane_land.wav")
        self.plane_crash_audio = Path("plane_crash.wav")

        # UI
        self.UI_draw_plane_keepout = False

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
        }

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
        LOG.info(f"Spawning plane '{id}' at {spawn_position}")
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
        v = Vector2(v.x * -1, v.y)
        v_screen = self.origin - v

        return v_screen

    def play_audio(self, audio):
        sound = pygame.mixer.Sound(str(self.assets_audio_path/audio))
        sound.set_volume(self.audio_volume)
        sound.play()

    def update(self):
        time = pygame.time.get_ticks()
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
    def __init__(self, id, position, heading, channels):
        self.id = id
        self.color = (0, 255, 0)
        self.position = Vector2(position)
        self.speed = 0.140  # km/s
        self.heading = (
            heading  # radians. zero is due north, positive angles counterclockwise.
        )
        self.status = "?"
        self.channels = channels
        self.transmit_frequency = 1  # Hz

        self.transmit = False

        self.shape = [Vector2(-0.1, 0), Vector2(0, 0.2), Vector2(0.1, 0)]
        self.transmit_time_prev = 0

        self.request_connection()

    def __str__(self):
        return f"Plane '{self.id}'\n\tPos: {self.position}\n\tHead: {self.heading}rad\n\tVel: {self.get_velocity()}"

    def get_velocity(self):
        return Vector2(math.cos(self.heading), math.sin(self.heading)) * self.speed

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
            telemetry={"position": self.position},
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

    def draw(self, surface, position_screen, scale):
        shape_oriented = [
            vertex.rotate(math.degrees(self.heading) - 90) for vertex in self.shape
        ]

        pygame.draw.polygon(
            surface=surface,
            color=self.color,
            points=((np.array(shape_oriented) + self.position) * scale)
            + position_screen,  # TODO: fix incorrecy y-axis rendering
            width=1,
        )


# pygame.time.set_timer(
#     event=event_transmission, millis=round(1 / self.transmit_frequency * 1000)
# )


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
