"""Main program entry script."""
# stdlib
import logging
import sys
from pathlib import Path

# external
import pygame

# project
from aatc import game

# region log config
log_path = Path("logs/main")
log_path.mkdir(parents=True, exist_ok=True)
handler_file = logging.FileHandler(
    filename=(log_path / Path(__file__).stem).with_suffix(".log"), mode="w"
)
handler_stdout = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[handler_file, handler_stdout],
)

LOG = logging.getLogger(__name__)
# endregion


def run():
    """Run the simulator."""

    GE = game.GameEngine()

    while True:

        # region event handling
        event_queue = pygame.event.get()
        for event in event_queue:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:  # print ATC state
                    LOG.info(GE.atc)
                    GE.play_audio(GE.user_interact_audio)

                elif event.key == pygame.K_F2:  # pause simulation
                    GE.paused = not GE.paused
                    LOG.info(f"Simulation paused: {GE.paused}")
                    GE.play_audio(GE.user_interact_audio)

                elif event.key == pygame.K_F3:  # toggle gizmos
                    GE.draw_gizmos = not GE.draw_gizmos
                    LOG.info(f"Drawing gizmos: {GE.draw_gizmos}")
                    GE.play_audio(GE.user_interact_audio)

                elif event.key == pygame.K_F4:  # print pygame event queue
                    LOG.debug(f"Event queue: {event_queue}")
                    GE.play_audio(GE.user_interact_audio)

                elif event.key == pygame.K_F12:  # debug function
                    plane_id = GE.atc.queue[0]
                    runway_id = GE.atc.get_nearest_open_runway_to_plane(plane_id)
                    LOG.info(f"Nearest open runway: {runway_id}")
                    GE.play_audio(GE.user_interact_audio)

                elif event.key == pygame.K_UP:  # pan up
                    LOG.debug("Panning up")
                    GE.origin[1] += GE.pan_amount * GE.screen_scale

                elif event.key == pygame.K_DOWN:  # pan down
                    LOG.debug("Panning down")
                    GE.origin[1] -= GE.pan_amount * GE.screen_scale

                elif event.key == pygame.K_LEFT:  # pan left
                    LOG.debug("Panning left")
                    GE.origin[0] += GE.pan_amount * GE.screen_scale

                elif event.key == pygame.K_RIGHT:  # pan right
                    LOG.debug("Panning right")
                    GE.origin[0] -= GE.pan_amount * GE.screen_scale

                elif event.key == pygame.K_KP_PLUS:  # zoom in
                    LOG.debug("Incrementing zoom")
                    GE.screen_scale += GE.zoom_amount

                elif event.key == pygame.K_KP_MINUS:  # zoom out
                    LOG.debug("Decrementing zoom")
                    GE.screen_scale -= GE.zoom_amount

            elif event.type == GE.events["CONNECTIONREQUEST"]:
                GE.atc.add_plane(event.plane_id)

            elif event.type == GE.events["CONNECTIONCONFIRMATION"]:
                plane = [plane for plane in GE.planes if plane.id == event.plane_id][
                    0
                ]  # TODO: find more efficient approach
                plane.transmit = True

            elif event.type == GE.events["TELEMETRY"]:
                GE.atc.update_telemetry(event.plane_id, event.telemetry)

            elif event.type == GE.events["FLIGHTPLAN"]:
                plane = [plane for plane in GE.planes if plane.id == event.plane_id][
                    0
                ]  # TODO: find more efficient approach

                plane.follow_plan(event.plan)

            elif event.type == GE.events["HOLD"]:
                plane = [plane for plane in GE.planes if plane.id == event.plane_id][
                    0
                ]  # TODO: find more efficient approach

                plane.hold()
        # endregion
        if not GE.paused:
            GE.update()
        GE.draw()


if __name__ == "__main__":
    run()
