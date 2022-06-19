# Copyright Iris contributors
#
# This file is part of Iris and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

"""Pytest fixtures for the gallery tests."""

import pathlib

import matplotlib.pyplot as plt
import pytest

import iris

CURRENT_DIR = pathlib.Path(__file__).resolve()
GALLERY_DIR = CURRENT_DIR.parents[1] / "gallery_code"


def _image_setup_teardown():
    """
    Setup and teardown fixture.

    Ensures all figures are closed before and after test to prevent one test
    polluting another if it fails with a figure unclosed.

    """
    plt.close("all")
    yield
    plt.close("all")


def _iris_future_defaults():
    """
    Create a fixture which resets all the iris.FUTURE settings to the defaults,
    as otherwise changes made in one test can affect subsequent ones.

    """
    # Run with all default settings in iris.FUTURE.
    default_future_kwargs = iris.Future().__dict__.copy()
    for dead_option in iris.Future.deprecated_options:
        # Avoid a warning when setting these !
        del default_future_kwargs[dead_option]
    with iris.FUTURE.context(**default_future_kwargs):
        yield


# Make function and class scoped fixtures.
image_setup_teardown = pytest.fixture(_image_setup_teardown)
class_image_setup_teardown = pytest.fixture(
    _image_setup_teardown, scope="class"
)

iris_future_defaults = pytest.fixture(_iris_future_defaults)
class_iris_future_defaults = pytest.fixture(
    _iris_future_defaults, scope="class"
)


@pytest.fixture(scope="module")
def import_patching():
    """
    Replace plt.show() with a function that does nothing, also add all the
    gallery examples to sys.path.  Done once for the whole test module.

    """

    def no_show():
        pass

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(plt, "show", no_show)
        for example_dir in GALLERY_DIR.iterdir():
            if example_dir.is_dir():
                mp.syspath_prepend(example_dir)

        yield
