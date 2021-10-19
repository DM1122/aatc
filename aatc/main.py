# stdlib
import logging
import sys
from pathlib import Path

# external
import controller
import game
import pygame

# paths
log_path = Path("logs/main")


# region logging
log_path.mkdir(parents=True, exist_ok=True)
handler_file = logging.FileHandler(
    filename=(log_path / Path(__file__).stem).with_suffix(".log"), mode="w"
)
handler_stdout = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[handler_file, handler_stdout],
)

LOG = logging.getLogger(__name__)
# endregion


if __name__ == "__main__":
    GE = game.GameEngine()
    ATC = controller.AATC(channels=GE.events)

    while True:
        event_queue = pygame.event.get()
        for event in event_queue:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    GE.UI_draw_plane_keepout = not GE.UI_draw_plane_keepout
                    LOG.info(f"UI plane keepout: {GE.UI_draw_plane_keepout}")
                elif event.key == pygame.K_F2:
                    LOG.info(ATC)
                elif event.key == pygame.K_F3:
                    LOG.debug(f"Event queue: {event_queue}")

            elif event.type == GE.events["CONNECTIONREQUEST"]:
                ATC.receive_connection(event.plane_id)

            elif event.type == GE.events["CONNECTIONCONFIRMATION"]:
                GE.planes[event.plane_id].transmit = True

            elif event.type == GE.events["TELEMETRY"]:
                ATC.update_telemetry(event.plane_id, event.telemetry)

            elif event.type == GE.events["FLIGHTPLAN"]:
                pass

        # draw scene
        GE.update()
        GE.draw()
