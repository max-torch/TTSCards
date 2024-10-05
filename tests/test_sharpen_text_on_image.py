from PIL import Image, ImageDraw
import pytesseract
import numpy as np
from scipy.ndimage import sobel
from pdf_generation import sharpen_text_on_image


def calculate_edge_intensity(image):
    # Convert image to grayscale
    gray_image = image.convert("L")
    # Convert grayscale image to numpy array
    image_array = np.array(gray_image)
    # Calculate the Sobel filter response
    edge_x = sobel(image_array, axis=0)
    edge_y = sobel(image_array, axis=1)
    edge_intensity = np.hypot(edge_x, edge_y)
    return edge_intensity.sum()


def test_sharpen_text_on_image_with_text():
    # Create an image with text
    image = Image.new("RGB", (100, 50), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Test", fill="black")

    # Calculate edge intensity before sharpening
    original_edge_intensity = calculate_edge_intensity(image)

    # Sharpen the text on the image
    result = sharpen_text_on_image(image)

    # Calculate edge intensity after sharpening
    sharpened_edge_intensity = calculate_edge_intensity(result)

    # Check if the result is still an image
    assert isinstance(result, Image.Image)

    # Check if the size of the image remains the same
    assert result.size == image.size

    # Check if the text is still present in the image
    result_text = pytesseract.image_to_string(result).strip()
    assert result_text == "Test"

    # Check if the edge intensity has increased
    assert sharpened_edge_intensity > original_edge_intensity


def test_sharpen_text_on_image_without_text():
    # Create an image without text
    image = Image.new("RGB", (100, 50), "white")

    # Calculate edge intensity before sharpening
    original_edge_intensity = calculate_edge_intensity(image)

    # Sharpen the text on the image
    result = sharpen_text_on_image(image)

    # Calculate edge intensity after sharpening
    sharpened_edge_intensity = calculate_edge_intensity(result)

    # Check if the result is still an image
    assert isinstance(result, Image.Image)

    # Check if the size of the image remains the same
    assert result.size == image.size

    # Check if no text is detected in the image
    result_text = pytesseract.image_to_string(result).strip()
    assert result_text == ""

    # Check if the edge intensity has not significantly increased
    assert sharpened_edge_intensity <= original_edge_intensity


def test_sharpen_text_on_image_with_colored_text():
    # Create an image with colored text
    image = Image.new("RGB", (100, 50), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Test", fill="blue")

    # Calculate edge intensity before sharpening
    original_edge_intensity = calculate_edge_intensity(image)

    # Sharpen the text on the image
    result = sharpen_text_on_image(image)

    # Calculate edge intensity after sharpening
    sharpened_edge_intensity = calculate_edge_intensity(result)

    # Check if the result is still an image
    assert isinstance(result, Image.Image)

    # Check if the size of the image remains the same
    assert result.size == image.size

    # Check if the text is still present in the image
    result_text = pytesseract.image_to_string(result).strip()
    assert result_text == "Test"

    # Check if the edge intensity has increased
    assert sharpened_edge_intensity > original_edge_intensity


def test_sharpen_text_on_image_with_large_text():
    # Create an image with large text
    image = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Large Text", fill="black")

    # Calculate edge intensity before sharpening
    original_edge_intensity = calculate_edge_intensity(image)

    # Sharpen the text on the image
    result = sharpen_text_on_image(image)

    # Calculate edge intensity after sharpening
    sharpened_edge_intensity = calculate_edge_intensity(result)

    # Check if the result is still an image
    assert isinstance(result, Image.Image)

    # Check if the size of the image remains the same
    assert result.size == image.size

    # Check if the text is still present in the image
    result_text = pytesseract.image_to_string(result).strip()
    assert result_text == "Large Text"

    # Check if the edge intensity has increased
    assert sharpened_edge_intensity > original_edge_intensity
