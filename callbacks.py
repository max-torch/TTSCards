import logging
import os


# Define preset page and card sizes in pixels at 300dpi
SHEET_SIZES = {
    "A4": (2480, 3508),
    "Letter": (2550, 3300),
    "Legal": (2550, 4200),
}
CARD_SIZES = {"standard": (734, 1045), "mini": (500, 734)}


# Create a logger for callbacks.py
logger = logging.getLogger("callbacks")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def start_script(
    filepath: str,
    cachepath: str,
    preset_image_size: tuple,
    custom_image_size_width: int,
    custom_image_size_length: int,
    sheet_size: tuple,
    outer_margin_size: float,
    inner_margin_size: float,
    dpi: int,
    verbose: bool,
    include_card_backs: bool,
    exclude_card_urls: bool,
    generate_bleed: bool,
    sharpen_text: bool,
    draw_cut_lines: bool,
    save_images: bool,
    load_images_from_directory: bool,
    arrange_into_pdf: bool,
) -> None:
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO) if verbose else logger.setLevel(logging.WARNING)

    logger.debug(f"filepath: {filepath}")
    logger.debug(f"cachepath: {cachepath}")
    logger.debug(f"preset_image_size: {preset_image_size}")
    logger.debug(f"custom_image_size_width: {custom_image_size_width}")
    logger.debug(f"custom_image_size_length: {custom_image_size_length}")
    logger.debug(f"sheet_size: {sheet_size}")
    logger.debug(f"outer_margin_size: {outer_margin_size}")
    logger.debug(f"inner_margin_size: {inner_margin_size}")
    logger.debug(f"dpi: {dpi}")
    logger.debug(f"verbose: {verbose}")
    logger.debug(f"include_card_backs: {include_card_backs}")
    logger.debug(f"exclude_card_urls: {exclude_card_urls}")
    logger.debug(f"generate_bleed: {generate_bleed}")
    logger.debug(f"sharpen_text: {sharpen_text}")
    logger.debug(f"draw_cut_lines: {draw_cut_lines}")
    logger.debug(f"save_images: {save_images}")
    logger.debug(f"load_images_from_directory: {load_images_from_directory}")
    logger.debug(f"arrange_into_pdf: {arrange_into_pdf}")

    # Create a variable `image_size` and set it to the preset image size if any of the custom image sizes are 0
    image_size = (
        CARD_SIZES[preset_image_size]
        if custom_image_size_width == 0 or custom_image_size_length == 0
        else (custom_image_size_width, custom_image_size_length)
    )
    logger.debug(f"image_size: {image_size}")
