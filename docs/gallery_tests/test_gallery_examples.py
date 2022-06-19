# Copyright Iris contributors
#
# This file is part of Iris and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

import importlib

import matplotlib.pyplot as plt
import pytest

from iris.tests import _RESULT_PATH
from iris.tests.graphics import check_graphic

from .conftest import GALLERY_DIR

TWO_FIG_EXAMPLES = [
    "plot_atlantic_profiles",
    "plot_cross_section",
    "plot_lagged_ensemble",
    "plot_wind_speed",
    "plot_projections_and_annotations",
]

FOUR_FIG_EXAMPLES = ["plot_orca_projection", "plot_rotated_pole_mapping"]


def gallery_examples():
    """Generator to yield all current gallery examples."""
    
    for example_file in GALLERY_DIR.glob("*/plot*.py"):
        yield example_file.stem


def expected_fignums(example_code):
    """How many figures we think are in each example."""
    if example_code in TWO_FIG_EXAMPLES:
        return 2
    elif example_code in FOUR_FIG_EXAMPLES:
        return 4
    else:
        return 1


def get_params():
    """
    Generator to yield sequence of (example, fig_number) pairs for gallery examples.
    Every figure from the examples is represented by one pair (except for the lagged
    ensemble example, which is handled separately).

    """
    for example in gallery_examples():
        if example == "plot_lagged_ensemble":
            continue
        else:
            for i in range(expected_fignums(example)):
                yield example, i


# Make a class for the GloSea example as it's particularly slow running, so we
# only want to run it once for the two tests.  Also define it before the other
# tests so it is queued up first.
@pytest.mark.xdist_group(name="group1")
class TestLagged:
    @pytest.fixture(scope="class")
    def get_figures(
        self,
        class_image_setup_teardown,
        class_iris_future_defaults,
        monkeypatching,
    ):

        module = importlib.import_module("plot_lagged_ensemble")
        module.main()

        figs = [plt.figure(fig_num) for fig_num in plt.get_fignums()]
        return figs

    @pytest.mark.filterwarnings("error::iris.IrisDeprecation")
    @pytest.mark.parametrize("fig_index", [0, 1], ids=lambda arg: f"fig{arg}")
    def test_lagged_example(self, get_figures, fig_index):
        assert len(get_figures) == 2
        plt.figure(get_figures[fig_index])
        image_id = f"gallery_tests.test_plot_lagged_ensemble.{fig_index}"
        check_graphic(image_id)


@pytest.mark.filterwarnings("error::iris.IrisDeprecation")
@pytest.mark.parametrize(
    "example", get_params(), ids=lambda arg: f"{arg[0]}-fig{arg[1]}"
)
def test_plot_example(
    example,
    image_setup_teardown,
    import_patches,
    iris_future_defaults,
    monkeypatching,
):
    """Test that all figures from example code match KGO."""

    example_code, fig_index = example
    module = importlib.import_module(example_code)

    # Run example.
    module.main()

    # Sanity check we have the right number of figures.
    assert len(plt.get_fignums()) == expected_fignums(example_code)

    # Compare chosen figure to KGO.
    plt.figure(fig_index + 1)
    image_id = f"gallery_tests.test_{example_code}.{fig_index}"
    check_graphic(image_id)
