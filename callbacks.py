import logging


# Define preset page and card sizes in pixels at 300dpi
SHEET_SIZES = {
    "A4": (2480, 3508),
    "Letter": (2550, 3300),
    "Legal": (2550, 4200),
}
CARD_SIZES = {"standard": (734, 1045), "mini": (500, 734)}


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
    logging.debug(f"filepath: {filepath}")
    logging.debug(f"cachepath: {cachepath}")
    logging.debug(f"preset_image_size: {preset_image_size}")
    logging.debug(f"custom_image_size_width: {custom_image_size_width}")
    logging.debug(f"custom_image_size_length: {custom_image_size_length}")
    logging.debug(f"sheet_size: {sheet_size}")
    logging.debug(f"outer_margin_size: {outer_margin_size}")
    logging.debug(f"inner_margin_size: {inner_margin_size}")
    logging.debug(f"dpi: {dpi}")
    logging.debug(f"verbose: {verbose}")
    logging.debug(f"include_card_backs: {include_card_backs}")
    logging.debug(f"exclude_card_urls: {exclude_card_urls}")
    logging.debug(f"generate_bleed: {generate_bleed}")
    logging.debug(f"sharpen_text: {sharpen_text}")
    logging.debug(f"draw_cut_lines: {draw_cut_lines}")
    logging.debug(f"save_images: {save_images}")
    logging.debug(f"load_images_from_directory: {load_images_from_directory}")
    logging.debug(f"arrange_into_pdf: {arrange_into_pdf}")

    # Create a variable `image_size` and set it to the preset image size if any of the custom image sizes are 0
    image_size = (
        CARD_SIZES[preset_image_size]
        if custom_image_size_width == 0 or custom_image_size_length == 0
        else (custom_image_size_width, custom_image_size_length)
    )
    logging.debug(f"image_size: {image_size}")
