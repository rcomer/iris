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


def expected_figcounts(example_code):
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
    Every figure from the examples is represented by one pair.

    """
    for example in gallery_examples():
        for i in range(expected_figcounts(example)):
            yield example, i


@pytest.mark.filterwarnings("error::iris.IrisDeprecation")
@pytest.mark.parametrize(
    "example", get_params(), ids=lambda arg: f"{arg[0]}-fig{arg[1]}"
)
def test_plot_example(
    example,
    image_setup_teardown,
    import_patches,
    iris_future_defaults,
    import_patching,
):
    """Test that all figures from example code match KGO."""

    example_code, fig_index = example
    module = importlib.import_module(example_code)

    # Run example.
    module.main()

    # Sanity check we have the right number of figures.
    assert len(plt.get_fignums()) == expected_figcounts(example_code)

    # Compare chosen figure to KGO.
    plt.figure(fig_index + 1)
    image_id = f"gallery_tests.test_{example_code}.{fig_index}"
    check_graphic(image_id)
