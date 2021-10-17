# stdlib
import logging
import sys
from pathlib import Path

# external
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

    GE.spawn_plane()
    GE.start_plane_spawn_timer()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    GE.UI_draw_plane_keepout = not GE.UI_draw_plane_keepout
                    LOG.info(f"UI plane keepout: {GE.UI_draw_plane_keepout}")

            if event.type == GE.SPAWNPLANEEVENT:
                GE.spawn_plane()
                GE.start_plane_spawn_timer()

        # draw scene
        GE.update()
        GE.draw()
