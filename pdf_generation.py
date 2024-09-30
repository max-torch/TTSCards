import logging
import os
import webbrowser

from PIL import Image, ImageDraw
from collections import namedtuple


Size = namedtuple("Size", ["width", "length"])


def generate_bleed_for_image(image: Image, bleed_size: int) -> Image:
    pass


def sharpen_text_on_image(image: Image) -> Image:
    pass


def draw_cut_lines_on_image(
    image: Image, x: int, y: int, card_size: Size, gutter_margin_size: int
):
    pass


def generate_pdf(
    images: list[Image.Image],
    output_dir: str,
    sheet_size: tuple,
    card_length: int,
    dpi: int,
    logger: logging.Logger,
    draw_cut_lines: bool,
    generate_bleed: bool,
    sharpen_text: bool,
    gutter_margin_size: float,
    filename: str,
):
    """
    images: list, a list of PIL Image objects representing the cards
    output_dir: str, the directory to save the generated PDF file
    sheet_size: tuple, the size of the sheet in pixels at 300dpi
    card_length: int, the length of the card in pixels at 300dpi
    dpi: int, the desired DPI for the output PDF file
    logger: logging.Logger, the logger object
    draw_cut_lines: bool, whether to draw cut lines on the PDF
    generate_bleed: bool, whether to generate bleed for each card
    sharpen_text: bool, whether to sharpen text on the cards
    gutter_margin_size: float, the size of the margin between cards in mm
    filename: str, the name of the output PDF file
    """

    # Convert card length, sheet size, and gutter margin size to pixels at the desired DPI
    converted_card_length = int(card_length * dpi / 300)
    converted_sheet_size = (
        int(sheet_size[0] * dpi / 300),
        int(sheet_size[1] * dpi / 300),
    )
    converted_gutter_margin_size = int(gutter_margin_size * dpi / 25.4)

    logger.debug(f"Converted card length: {converted_card_length}")
    logger.debug(f"Converted sheet size: {converted_sheet_size}")
    logger.debug(f"Converted gutter margin size: {converted_gutter_margin_size}")

    # Calculate what the width of the first card would be after resizing to card_length while maintaining aspect ratio
    first_card_size = images[0].size
    card_width = int(converted_card_length * first_card_size[0] / first_card_size[1])
    logger.debug(f"Card width: {card_width}")

    # Calculate the number of cards that can fit on the sheet
    num_cards_x = (
        converted_sheet_size[0] - 2 * converted_gutter_margin_size
    ) // card_width
    num_cards_y = (
        converted_sheet_size[1] - 2 * converted_gutter_margin_size
    ) // converted_card_length

    # Calculate the number of sheets required to fit all the cards
    num_sheets = (len(images) + num_cards_x * num_cards_y - 1) // (
        num_cards_x * num_cards_y
    )

    # Calculate the size of the entire grid of cards, including gutters
    grid_size = (
        num_cards_x * card_width + 2 * converted_gutter_margin_size,
        num_cards_y * converted_card_length + 2 * converted_gutter_margin_size,
    )
    logger.debug(f"Grid size: {grid_size}")

    # Calculate the starting position to center the grid on the sheet
    start_x = (converted_sheet_size[0] - grid_size[0]) // 2
    start_y = (converted_sheet_size[1] - grid_size[1]) // 2

    # Paste the cards onto the sheets
    sheets = []

    for i in range(num_sheets):
        sheet = Image.new("RGB", converted_sheet_size, "white")
        draw = ImageDraw.Draw(sheet)

        for j in range(num_cards_x * num_cards_y):
            if i * num_cards_x * num_cards_y + j >= len(images):
                break

            card = images[i * num_cards_x * num_cards_y + j]

            # Resize the card to the desired length while maintaining aspect ratio
            card = card.resize((card_width, converted_card_length), Image.LANCZOS)

            # Generate bleed for the card
            if generate_bleed:
                card = generate_bleed_for_image(card, 5)

            # Sharpen text on the card
            if sharpen_text:
                card = sharpen_text_on_image(card)

            # Paste the card onto the sheet
            x = start_x + (j % num_cards_x) * (
                card_width + converted_gutter_margin_size
            )
            y = start_y + (j // num_cards_x) * (
                converted_card_length + converted_gutter_margin_size
            )
            logger.debug(
                f"Pasting card {i * num_cards_x * num_cards_y + j} at ({x}, {y})"
            )
            sheet.paste(card, (x, y))

            # Draw cut lines on the sheet
            if draw_cut_lines:
                draw_cut_lines_on_image(
                    draw,
                    x,
                    y,
                    Size(card_width, converted_card_length),
                    converted_gutter_margin_size,
                )

        sheets.append(sheet)

    # Generate a PDF file from the sheets
    pdf_filename = os.path.join(f"{output_dir}/pdf", filename)
    os.makedirs(f"{output_dir}/pdf", exist_ok=True)
    sheets[0].save(
        pdf_filename,
        format="PDF",
        save_all=True,
        append_images=sheets[1:],
        resolution=dpi,
    )
    logger.info(f"PDF file saved to {pdf_filename}")

    # Open the generated PDF file in the default PDF viewer
    webbrowser.open_new(pdf_filename)
