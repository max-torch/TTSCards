import pytest
import pytesseract
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
from pdf_generation import generate_pdf, Size


@pytest.fixture
def sample_images() -> list[Image.Image]:
    images = []
    for i in range(5):
        # image = Image.new("RGB", (3060, 3960), (255, 255, 255))
        # draw = ImageDraw.Draw(image)
        # draw.text((100, 100), f"Test {i + 1}", fill="black", font=None, anchor=None)
        image = Image.new("RGB", (100, 50), "white")
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Test", fill="black")
        images.append(image)

    return images


@pytest.fixture
def logger() -> MagicMock:
    # Create a mock logger
    return MagicMock()


@patch("pdf_generation.webbrowser.open_new")
@patch("pdf_generation.os.makedirs")
@patch("pdf_generation.Image.Image.save")
def test_generate_pdf_basic(
    mock_save: MagicMock,
    mock_makedirs: MagicMock,
    mock_open_new: MagicMock,
    sample_images: list[Image.Image],
    logger: MagicMock,
):
    generate_pdf(
        images=sample_images,
        output_dir="output",
        sheet_size=(3060, 3960),
        card_length=1254,
        dpi=300,
        logger=logger,
        draw_cut_lines=False,
        generate_bleed=False,
        sharpen_text=False,
        gutter_margin_size=5,
        filename="test.pdf",
        cut_lines_on_margin_only=False,
    )
    mock_save.assert_called_once()
    mock_makedirs.assert_called_once_with("output/pdf", exist_ok=True)
    mock_open_new.assert_called_once()


@patch("pdf_generation.webbrowser.open_new")
@patch("pdf_generation.os.makedirs")
@patch("pdf_generation.Image.Image.save")
def test_generate_pdf_with_bleed(
    mock_save: MagicMock,
    mock_makedirs: MagicMock,
    mock_open_new: MagicMock,
    sample_images: list[Image.Image],
    logger: MagicMock,
):
    generate_pdf(
        images=sample_images,
        output_dir="output",
        sheet_size=(3060, 3960),
        card_length=1254,
        dpi=300,
        logger=logger,
        draw_cut_lines=False,
        generate_bleed=True,
        sharpen_text=False,
        gutter_margin_size=5,
        filename="test_bleed.pdf",
        cut_lines_on_margin_only=False,
    )
    mock_save.assert_called_once()
    mock_makedirs.assert_called_once_with("output/pdf", exist_ok=True)
    mock_open_new.assert_called_once()


@patch("pdf_generation.webbrowser.open_new")
@patch("pdf_generation.os.makedirs")
@patch("pdf_generation.Image.Image.save")
def test_generate_pdf_with_sharpen_text(
    mock_save: MagicMock,
    mock_makedirs: MagicMock,
    mock_open_new: MagicMock,
    sample_images: list[Image.Image],
    logger: MagicMock,
):
    generate_pdf(
        images=sample_images,
        output_dir="output",
        sheet_size=(3060, 3960),
        card_length=1254,
        dpi=300,
        logger=logger,
        draw_cut_lines=False,
        generate_bleed=False,
        sharpen_text=True,
        gutter_margin_size=5,
        filename="test_sharpen.pdf",
        cut_lines_on_margin_only=False,
    )
    mock_save.assert_called_once()
    mock_makedirs.assert_called_once_with("output/pdf", exist_ok=True)
    mock_open_new.assert_called_once()


@patch("pdf_generation.webbrowser.open_new")
@patch("pdf_generation.os.makedirs")
@patch("pdf_generation.Image.Image.save")
def test_generate_pdf_with_cut_lines(
    mock_save: MagicMock,
    mock_makedirs: MagicMock,
    mock_open_new: MagicMock,
    sample_images: list[Image.Image],
    logger: MagicMock,
):
    generate_pdf(
        images=sample_images,
        output_dir="output",
        sheet_size=(3060, 3960),
        card_length=1254,
        dpi=300,
        logger=logger,
        draw_cut_lines=True,
        generate_bleed=False,
        sharpen_text=False,
        gutter_margin_size=5,
        filename="test_cut_lines.pdf",
        cut_lines_on_margin_only=False,
    )
    mock_save.assert_called_once()
    mock_makedirs.assert_called_once_with("output/pdf", exist_ok=True)
    mock_open_new.assert_called_once()


@patch("pdf_generation.webbrowser.open_new")
@patch("pdf_generation.os.makedirs")
@patch("pdf_generation.Image.Image.save")
def test_generate_pdf_with_all_options(
    mock_save: MagicMock,
    mock_makedirs: MagicMock,
    mock_open_new: MagicMock,
    sample_images: list[Image.Image],
    logger: MagicMock,
):
    generate_pdf(
        images=sample_images,
        output_dir="output",
        sheet_size=(3060, 3960),
        card_length=1254,
        dpi=300,
        logger=logger,
        draw_cut_lines=True,
        generate_bleed=True,
        sharpen_text=True,
        gutter_margin_size=5,
        filename="test_all_options.pdf",
        cut_lines_on_margin_only=True,
    )
    mock_save.assert_called_once()
    mock_makedirs.assert_called_once_with("output/pdf", exist_ok=True)
    mock_open_new.assert_called_once()
