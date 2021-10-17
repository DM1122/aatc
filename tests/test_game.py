"""Tests for game object functionality."""
# stdlib
import logging

# external
import numpy as np
import pygame
from pygame.math import Vector2

# project
from aatc import game

LOG = logging.getLogger(__name__)


def test_gameengine_vector_to_screen():
    """Test vector_to_screen()."""
    GE = game.GameEngine(screen_size=(100, 100))

    vector = Vector2(1, 1)
    LOG.info(f"Vector in game coordinates: {vector}, ({type(vector)})")

    vector_screen = GE.vector_to_screen(vector)
    LOG.info(f"Vector in screen coordinates: {vector_screen}, ({type(vector_screen)})")

    assert vector_screen == (51, 49)


# def test_gameengine_spawn_plane():
#     """Test spawn_plane()."""
#     GE = game.GameEngine(screen_size=(500, 500))
#     GE.spawn_plane()
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()

#         GE.draw()
