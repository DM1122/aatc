"""Tests for game object functionality."""
# stdlib
import logging

# external
from pygame.math import Vector2

# project
from aatc import game

LOG = logging.getLogger(__name__)


def test_gameengine_vector_to_screen():
    """Test vector_to_screen()."""
    GE = game.GameEngine(screen_size=(100, 100))
    GE.screen_scale = 2  # px per unit

    LOG.info(f"Screen scale: {GE.screen_scale}")

    vector = Vector2(1, 1)
    LOG.info(f"Vector in game coordinates: {vector}, ({type(vector)})")

    vector_screen = GE.vector_to_screen(vector)
    LOG.info(f"Vector in screen coordinates: {vector_screen}, ({type(vector_screen)})")

    assert vector_screen == (52, 48)
