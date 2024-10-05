import pytest
from PIL import Image, ImageChops
from pdf_generation import draw_cut_lines_on_sheet, Size


@pytest.fixture
def blank_sheet():
    # Create a blank white sheet for testing
    return Image.new("RGB", (100, 100), "white")


def test_draw_cut_lines_on_sheet_with_bleed(blank_sheet):
    # Test drawing cut lines with bleed
    draw_cut_lines_on_sheet(
        generate_bleed=True,
        converted_card_length=20,
        converted_sheet_size=(100, 100),
        converted_gutter_margin_size=5,
        card_width=15,
        no_bleed_card_size=Size(15, 20),
        converted_bleed_size=2,
        num_cards_x=3,
        num_cards_y=3,
        start_x=10,
        start_y=10,
        sheet=blank_sheet,
        line_width=1,
    )
    # Check if lines are drawn (not a blank image anymore)
    assert (
        not ImageChops.difference(
            blank_sheet, Image.new("RGB", (100, 100), "white")
        ).getbbox()
        is None
    )


def test_draw_cut_lines_on_sheet_without_bleed(blank_sheet):
    # Test drawing cut lines without bleed
    draw_cut_lines_on_sheet(
        generate_bleed=False,
        converted_card_length=20,
        converted_sheet_size=(100, 100),
        converted_gutter_margin_size=5,
        card_width=15,
        no_bleed_card_size=Size(15, 20),
        converted_bleed_size=0,
        num_cards_x=3,
        num_cards_y=3,
        start_x=10,
        start_y=10,
        sheet=blank_sheet,
        line_width=1,
    )
    # Check if lines are drawn (not a blank image anymore)
    assert (
        not ImageChops.difference(
            blank_sheet, Image.new("RGB", (100, 100), "white")
        ).getbbox()
        is None
    )


def test_draw_cut_lines_on_sheet_with_different_line_width(blank_sheet):
    # Test drawing cut lines with different line width
    draw_cut_lines_on_sheet(
        generate_bleed=True,
        converted_card_length=20,
        converted_sheet_size=(100, 100),
        converted_gutter_margin_size=5,
        card_width=15,
        no_bleed_card_size=Size(15, 20),
        converted_bleed_size=2,
        num_cards_x=3,
        num_cards_y=3,
        start_x=10,
        start_y=10,
        sheet=blank_sheet,
        line_width=3,
    )
    # Check if lines are drawn (not a blank image anymore)
    assert (
        not ImageChops.difference(
            blank_sheet, Image.new("RGB", (100, 100), "white")
        ).getbbox()
        is None
    )


def test_draw_cut_lines_on_sheet_with_margin_only(blank_sheet):
    # Test drawing cut lines on margin only
    draw_cut_lines_on_sheet(
        generate_bleed=True,
        converted_card_length=20,
        converted_sheet_size=(100, 100),
        converted_gutter_margin_size=5,
        card_width=15,
        no_bleed_card_size=Size(15, 20),
        converted_bleed_size=2,
        num_cards_x=3,
        num_cards_y=3,
        start_x=10,
        start_y=10,
        sheet=blank_sheet,
        line_width=1,
    )
    # Check if lines are drawn (not a blank image anymore)
    assert (
        not ImageChops.difference(
            blank_sheet, Image.new("RGB", (100, 100), "white")
        ).getbbox()
        is None
    )


def test_draw_cut_lines_on_sheet_with_large_sheet(blank_sheet):
    # Test drawing cut lines on a larger sheet
    large_sheet = Image.new("RGB", (200, 200), "white")
    draw_cut_lines_on_sheet(
        generate_bleed=True,
        converted_card_length=40,
        converted_sheet_size=(200, 200),
        converted_gutter_margin_size=10,
        card_width=30,
        no_bleed_card_size=Size(30, 40),
        converted_bleed_size=4,
        num_cards_x=4,
        num_cards_y=4,
        start_x=20,
        start_y=20,
        sheet=large_sheet,
        line_width=2,
    )
    # Check if lines are drawn (not a blank image anymore)
    assert (
        not ImageChops.difference(
            large_sheet, Image.new("RGB", (200, 200), "white")
        ).getbbox()
        is None
    )
