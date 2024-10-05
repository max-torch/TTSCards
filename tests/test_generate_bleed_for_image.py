import pytest
from PIL import Image
import numpy as np
from pdf_generation import generate_bleed_for_image


@pytest.fixture
def red_image():
    # Create a simple 10x10 red image for testing
    return Image.new("RGB", (10, 10), "red")


def test_bleed_size_0(red_image):
    # Test with bleed size 0, should return the same image
    result = generate_bleed_for_image(red_image, 0)
    assert result.size == red_image.size
    assert np.array_equal(np.array(result), np.array(red_image))


def test_bleed_size_2(red_image):
    # Test with bleed size 2
    bleed_size = 2
    result = generate_bleed_for_image(red_image, bleed_size)
    expected_size = (
        red_image.width + 2 * bleed_size,
        red_image.height + 2 * bleed_size,
    )
    assert result.size == expected_size

    # Check if the original image is correctly placed in the center
    center_region = result.crop(
        (
            bleed_size,
            bleed_size,
            bleed_size + red_image.width,
            bleed_size + red_image.height,
        )
    )
    assert np.array_equal(np.array(center_region), np.array(red_image))


def test_bleed_size_5(red_image):
    # Test with bleed size 5
    bleed_size = 5
    result = generate_bleed_for_image(red_image, bleed_size)
    expected_size = (
        red_image.width + 2 * bleed_size,
        red_image.height + 2 * bleed_size,
    )
    assert result.size == expected_size

    # Check if the original image is correctly placed in the center
    center_region = result.crop(
        (
            bleed_size,
            bleed_size,
            bleed_size + red_image.width,
            bleed_size + red_image.height,
        )
    )
    assert np.array_equal(np.array(center_region), np.array(red_image))


def test_bleed_with_non_square_image():
    # Create a simple 10x20 blue image for testing
    image = Image.new("RGB", (10, 20), "blue")
    bleed_size = 3
    result = generate_bleed_for_image(image, bleed_size)
    expected_size = (image.width + 2 * bleed_size, image.height + 2 * bleed_size)
    assert result.size == expected_size

    # Check if the original image is correctly placed in the center
    center_region = result.crop(
        (bleed_size, bleed_size, bleed_size + image.width, bleed_size + image.height)
    )
    assert np.array_equal(np.array(center_region), np.array(image))


def test_bleed_with_large_bleed_size():
    # Create a simple 10x10 green image for testing
    image = Image.new("RGB", (10, 10), "green")
    bleed_size = 10
    result = generate_bleed_for_image(image, bleed_size)
    expected_size = (image.width + 2 * bleed_size, image.height + 2 * bleed_size)
    assert result.size == expected_size

    # Check if the original image is correctly placed in the center
    center_region = result.crop(
        (bleed_size, bleed_size, bleed_size + image.width, bleed_size + image.height)
    )
    assert np.array_equal(np.array(center_region), np.array(image))
