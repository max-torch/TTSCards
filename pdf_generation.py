import logging
import os
import webbrowser

from PIL import Image, ImageDraw
from collections import namedtuple


Size = namedtuple("Size", ["width", "length"])


def generate_bleed_for_image(image: Image.Image, bleed_size: int) -> Image.Image:
    """
    image: PIL Image object, the image to generate bleed for
    bleed_size: int, the size of the bleed in pixels
    """
    # Select rectangular regions at the four edges of the image
    left_region = image.crop((0, 0, bleed_size, image.height))
    bottom_region = image.crop(
        (0, image.height - bleed_size, image.width, image.height)
    )
    right_region = image.crop((image.width - bleed_size, 0, image.width, image.height))
    top_region = image.crop((0, 0, image.width, bleed_size))

    # Create a new image with the size of the original image plus the bleed size
    new_image = Image.new(
        "RGB", (image.width + 2 * bleed_size, image.height + 2 * bleed_size), "white"
    )

    # Paste the original image onto the new image with an offset of the bleed size
    new_image.paste(image, (bleed_size, bleed_size))

    # Paste the mirrored over rectangular regions onto the new image
    new_image.paste(left_region.transpose(Image.FLIP_LEFT_RIGHT), (0, bleed_size))
    new_image.paste(
        bottom_region.transpose(Image.FLIP_TOP_BOTTOM),
        (bleed_size, image.height + bleed_size),
    )
    new_image.paste(
        right_region.transpose(Image.FLIP_LEFT_RIGHT),
        (image.width + bleed_size, bleed_size),
    )
    new_image.paste(top_region.transpose(Image.FLIP_TOP_BOTTOM), (bleed_size, 0))

    return new_image


def sharpen_text_on_image(image: Image) -> Image:
    pass


def draw_cut_lines_on_sheet(
    generate_bleed,
    converted_card_length,
    converted_sheet_size,
    converted_gutter_margin_size,
    card_width,
    no_bleed_card_size,
    converted_bleed_size,
    num_cards_x,
    num_cards_y,
    start_x,
    start_y,
    sheet,
):
    draw = ImageDraw.Draw(sheet, "RGBA")
    line_color = (0, 0, 0, 128)
    line_width = 1
    small_margin = 5  # Small margin from the edges of the sheet in pixels

    # Draw horizontal cut lines at the top edges of each card, considering the number of cards
    bleed_adjustment = converted_bleed_size if generate_bleed else 0

    # top edge of cards
    for j in range(num_cards_y):
        y = (
            start_y
            + bleed_adjustment
            + j * (converted_card_length + converted_gutter_margin_size)
        )
        draw.line(
            [(small_margin, y), (converted_sheet_size[0] - small_margin, y)],
            fill=line_color,
            width=line_width,
        )

        # bottom edge of cards
    for j in range(num_cards_y):
        y = (
            start_y
            + bleed_adjustment
            + no_bleed_card_size.length
            + j * (converted_card_length + converted_gutter_margin_size)
        )
        draw.line(
            [(small_margin, y), (converted_sheet_size[0] - small_margin, y)],
            fill=line_color,
            width=line_width,
        )

        # left edge of cards
    for j in range(num_cards_x):
        x = start_x + bleed_adjustment + j * (card_width + converted_gutter_margin_size)
        draw.line(
            [(x, small_margin), (x, converted_sheet_size[1] - small_margin)],
            fill=line_color,
            width=line_width,
        )

        # right edge of cards
    for j in range(num_cards_x):
        x = (
            start_x
            + bleed_adjustment
            + no_bleed_card_size.width
            + j * (card_width + converted_gutter_margin_size)
        )
        draw.line(
            [(x, small_margin), (x, converted_sheet_size[1] - small_margin)],
            fill=line_color,
            width=line_width,
        )


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
    cut_lines_on_margin_only: bool,
    bleed_size: float = 2.0,
    no_cut_lines_on_last_sheet: bool = False,
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
    bleed_size: float, the size of the bleed in mm
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

    # Save the card size before adding bleed
    no_bleed_card_size = Size(card_width, converted_card_length)

    converted_bleed_size = 0
    if generate_bleed:
        converted_bleed_size = int(bleed_size * dpi / 25.4)
        logger.debug(f"Converted bleed size: {converted_bleed_size}")

        # Calculate what the size of the first card would be after adding bleed
        card_width += 2 * converted_bleed_size
        converted_card_length += 2 * converted_bleed_size
        logger.debug(f"Card width with bleed: {card_width}")
        logger.debug(f"Card length with bleed: {converted_card_length}")

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

        if (
            draw_cut_lines
            and cut_lines_on_margin_only
            and (not no_cut_lines_on_last_sheet or i < num_sheets - 1)
        ):
            draw_cut_lines_on_sheet(
                generate_bleed,
                converted_card_length,
                converted_sheet_size,
                converted_gutter_margin_size,
                card_width,
                no_bleed_card_size,
                converted_bleed_size,
                num_cards_x,
                num_cards_y,
                start_x,
                start_y,
                sheet,
            )

        for j in range(num_cards_x * num_cards_y):
            if i * num_cards_x * num_cards_y + j >= len(images):
                break

            card = images[i * num_cards_x * num_cards_y + j]

            # Resize the card to the desired length while maintaining aspect ratio
            card = card.resize(no_bleed_card_size, Image.LANCZOS)

            # Generate bleed for the card
            if generate_bleed:
                card = generate_bleed_for_image(card, converted_bleed_size)

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

        if (
            draw_cut_lines
            and not cut_lines_on_margin_only
            and (not no_cut_lines_on_last_sheet or i < num_sheets - 1)
        ):
            draw_cut_lines_on_sheet(
                generate_bleed,
                converted_card_length,
                converted_sheet_size,
                converted_gutter_margin_size,
                card_width,
                no_bleed_card_size,
                converted_bleed_size,
                num_cards_x,
                num_cards_y,
                start_x,
                start_y,
                sheet,
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
