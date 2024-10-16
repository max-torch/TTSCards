import json
import logging
import os
import re
from urllib.request import urlopen

from PIL import Image

from pdf_generation import generate_pdf


# Define custom exceptions
class ImageFilesNotFoundError(Exception):
    """Raised when the image files are not found in the specified directory."""

    def __init__(self, message="No image files were found in the specified directory. No output was generated."):
        self.message = message
        super().__init__(self.message)


class CardsNotFoundError(Exception):
    """Raised when no cards are found in the TTS Saved Object data."""

    def __init__(self, message="No cards were found in the TTS Saved Object data. No output was generated."):
        self.message = message
        super().__init__(self.message)


# Define preset card sizes in pixels at 300dpi
SHEET_SIZES = {
    "A4": (2480, 3508),
    "Letter": (2550, 3300),
    "Legal": (2550, 4200),
}
CARD_SIZES = {"standard": (734, 1045), "mini": (500, 734)}

# Create a logger for card_saving_and_loading.py
logger = logging.getLogger("main")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(levelname)s: %(message)s")  # noqa; because the levelname is not a typo in this context
handler.setFormatter(formatter)
logger.addHandler(handler)


def download_image(url: str, blacklist: list[str], cache_folder: str) -> Image:
    """
    Downloads an image from a given URL, with caching and blacklist support.

    Args:
        url (str): The URL of the image to download.
        blacklist (list[str]): A list of URLs that should be skipped.
        cache_folder (str): The folder where cached images are stored.

    Returns:
        Image: The downloaded image, or None if the URL is blacklisted.

    The function first checks if the URL is in the blacklist. If it is, it logs a debug message and returns None.
    It then formats the URL to create a cache file name and checks if the image is already cached in the specified folder.
    If the image is cached, it opens and returns the cached image. If not, it downloads the image, saves it to the cache folder,
    and then returns the downloaded image.
    """
    if url in blacklist:
        logger.debug(f"Skipping URL (blacklisted): {url}")
        return None

    def format_url(url_string):
        for char in [
            ":",
            "/",
            ".",
            "-",
        ]:
            url_string = url_string.replace(char, "")
        return url_string

    # Check if the image file is saved locally in the cache folder
    cache_file_name = format_url(url)
    cache_file_path_png = os.path.join(cache_folder, cache_file_name + ".png")
    cache_file_path_jpg = os.path.join(cache_folder, cache_file_name + ".jpg")

    if os.path.exists(cache_file_path_png):
        # Open the PNG image file
        img = Image.open(cache_file_path_png)
    elif os.path.exists(cache_file_path_jpg):
        # Open the JPG image file
        img = Image.open(cache_file_path_jpg)
    else:
        # Open the image file
        img = Image.open(urlopen(url))

        # Save the image file to the cache folder
        os.makedirs(cache_folder, exist_ok=True)
        img.save(cache_file_path_png, "PNG")
        logger.info(f"Saved PNG image to cache: {cache_file_path_png}")

    return img


def crop_from_sprite_sheet(
        sprite_sheet: Image, num_width: int, num_height: int, card_id: int
) -> Image:
    """
    Crop a specific card from a sprite sheet based on its ID.

    Args:
        sprite_sheet (Image): The sprite sheet image containing multiple cards.
        num_width (int): The number of cards horizontally in the sprite sheet.
        num_height (int): The number of cards vertically in the sprite sheet.
        card_id (int): The ID of the card to be cropped. The last two digits of the ID are used to determine the card's position.

    Returns:
        Image: The cropped card image.
    """
    # calculate the position of the card in the sprite sheet
    sheet_width, sheet_height = sprite_sheet.size
    card_width = sheet_width // num_width
    card_height = sheet_height // num_height
    card_index = int(str(card_id)[-2:])
    x_coordinate = card_index % num_width
    y_coordinate = card_index // num_width

    # calculate the bounding box of the card
    left = x_coordinate * card_width
    top = y_coordinate * card_height
    right = left + card_width
    bottom = top + card_height

    # crop the card from the sprite sheet
    card = sprite_sheet.crop((left, top, right, bottom))

    return card


def process_deck(deck: dict, blacklist: list, cachepath: str, exclude_card_backs: bool) -> list[dict]:
    """
    Processes a deck of cards, filtering out blacklisted items and caching images.

    Args:
        deck (dict): The deck of cards to process, expected to have a "ContainedObjects" key.
        blacklist (list): A list of items to be excluded from processing.
        cachepath (str): The path where cached images should be stored.
        exclude_card_backs (bool): Flag to exclude card backs from processing.

    Returns:
        list[dict]: A list of dictionaries containing processed card images.
    """
    contained_objects = deck.get("ContainedObjects", {})
    images = []
    for card in contained_objects:
        card_images = process_card(card, blacklist, cachepath, exclude_card_backs)
        images.append(card_images)
    logger.info(f"Processed deck containing {len(images)} cards")
    return images


def process_card(card: dict, blacklist: list, cachepath: str, exclude_card_backs) -> dict:
    """
    Processes a card dictionary to download and split the sprite sheet for the deck.

    Args:
        card (dict): A dictionary containing card information, including "Nickname", "CardID", and "CustomDeck".
        blacklist (list): A list of URLs to be blacklisted from downloading.
        cachepath (str): The path to the cache directory for storing downloaded images.
        exclude_card_backs (bool): Flag to exclude card backs from processing.

    Returns:
        dict: A dictionary containing the processed card images with keys "face" and "back".
    """
    nickname = card.get("Nickname", "")
    card_id = card.get("CardID", 0)
    custom_deck = card.get("CustomDeck", {})
    custom_deck_key = list(custom_deck)[0]
    face_url = custom_deck[custom_deck_key].get("FaceURL", "")
    back_url = custom_deck[custom_deck_key].get("BackURL", "")
    num_width = custom_deck[custom_deck_key].get("NumWidth", 1)
    num_height = custom_deck[custom_deck_key].get("NumHeight", 1)
    unique_back = custom_deck[custom_deck_key].get("UniqueBack", False)

    # Download and split the sprite sheet for the deck
    image = {}
    if face_url:
        sprite_sheet = download_image(face_url, blacklist, cachepath)
        if sprite_sheet:
            card_face = crop_from_sprite_sheet(
                sprite_sheet, num_width, num_height, card_id
            )
            image["face"] = card_face

    if back_url and not exclude_card_backs:
        sprite_sheet = download_image(back_url, blacklist, cachepath)
        if unique_back:
            image["back"] = crop_from_sprite_sheet(
                sprite_sheet, num_width, num_height, card_id + 1000
            )
        elif sprite_sheet:
            image["back"] = sprite_sheet

    logger.info(f"Processed card: {nickname}")
    return image


def process_bag(
        bag: dict, blacklist: list, cachepath: str, process_nested: bool, exclude_card_backs: bool
) -> list[dict]:
    """
    Processes a bag object, extracting images from contained objects.

    Args:
        bag (dict): The bag object to process.
        blacklist (list): List of blacklisted items to exclude from processing.
        cachepath (str): Path to the cache directory.
        process_nested (bool): Flag to determine if nested containers should be processed.
        exclude_card_backs (bool): Flag to exclude card backs from processing.

    Returns:
        list[dict]: A list of dictionaries containing image data extracted from the bag.
    """
    contained_objects = bag.get("ContainedObjects", [])
    images = []
    for tts_object in contained_objects:
        if tts_object.get("Name") == "Deck":
            logger.info(f"Processing deck: {tts_object.get('Nickname', 'Unknown Deck')}")
            images.extend(process_deck(tts_object, blacklist, cachepath, exclude_card_backs))
        elif tts_object.get("Name") == "Card":
            logger.info(f"Processing card: {tts_object.get('Nickname', 'Unknown Card')}")
            images.append(process_card(tts_object, blacklist, cachepath, exclude_card_backs))
        elif tts_object.get("Name") == "Bag" and process_nested:
            logger.info(f"Processing bag: {tts_object.get('Nickname', 'Unknown Bag')}")
            images.extend(process_bag(tts_object, blacklist, cachepath, process_nested, exclude_card_backs))

    return images


def process_tts_object(
        tts_object, process_nested_containers, blacklist, cachepath: str, exclude_card_backs: bool,
) -> list[dict]:
    """
    Processes a TTS object and its nested objects, extracting images and handling different object types.
    Can only handle objects of type "Deck", "Card", and "Bag".

    Args:
        tts_object (dict): The TTS object to process.
        process_nested_containers (bool): Flag to determine if nested containers should be processed.
        blacklist (list): List of blacklisted items to exclude from processing.
        cachepath (str): Path to the cache directory.
        exclude_card_backs (bool): Flag to exclude card backs from processing.

    Returns:
        list[dict]: A list of dictionaries containing image data extracted from the container.
    """
    object_states = tts_object.get("ObjectStates", [])

    images = []
    for state in object_states:
        obj_name = state.get("Name", "")
        if obj_name == "Deck":  # Process deck
            logger.info(f"Processing deck: {state.get('Nickname', 'Unknown Deck')}")
            images.extend(process_deck(state, blacklist, cachepath, exclude_card_backs))
        elif obj_name == "Card":  # Process single card
            logger.info(f"Processing card: {state.get('Nickname', 'Unknown Card')}")
            images.append(process_card(state, blacklist, cachepath, exclude_card_backs))
        elif obj_name == "Bag":  # Process container (Bag)
            logger.info(f"Processing bag: {state.get('Nickname', 'Unknown Bag')}")
            images.extend(
                process_bag(state, blacklist, cachepath, process_nested_containers, exclude_card_backs)
            )
        else:
            logger.warning(f"Unknown object type: {obj_name}")

    return images


def load_images(output_directory: str) -> list[dict]:
    """
    Loads images from the specified output directory, sorts them, and categorizes them into 'face' and 'back' images.

    Args:
        output_directory (str): The directory where the image files are located.

    Returns:
        list[dict]: A list of dictionaries containing the loaded images. Each dictionary has a key 'face' or 'back'
                    corresponding to the type of image.
    """
    images = []
    image_files = sorted(
        [
            file
            for file in os.listdir(output_directory)
            if file.endswith(".png") or file.endswith(".jpg")
        ],
        key=lambda file: [
            int(text) if text.isdigit() else text for text in re.split(r"(\d+)", file)
        ],
    )
    for filename in image_files:
        image = Image.open(f"{output_directory}/{filename}")
        if "_face" in filename:
            images.append({"face": image})
        elif "_back" in filename:
            images.append({"back": image})
        else:
            # If the image name doesn't conform, treat is as a face image
            images.append({"face": image})

    return images


def start_script(
        output_directory: str,
        path: str,
        cachepath: str,
        preset_image_size: str,
        custom_image_size_length: float,
        sheet_size: str,
        custom_sheet_width: float,
        custom_sheet_length: float,
        gutter_margin_size: float,
        dpi: int,
        verbose: bool,
        process_nested_containers: bool,
        exclude_card_urls: bool,
        exclude_card_backs: bool,
        generate_bleed: bool,
        sharpen_text: bool,
        draw_cut_lines: bool,
        split_double_and_single: bool,
        double_only: bool,
        single_only: bool,
        save_images: bool,
        skip_pdf_generation: bool,
        cut_lines_on_margin_only: bool,
        no_cut_lines_on_last_sheet: bool,
        bleed_width: float,
        line_width: int,
) -> None:
    """
    Starts the script to process images and arrange them into a PDF.

    Args:
        output_directory (str): Path to the output directory
        path (str): Path to the input file containing TTS Saved Object data or folder containing images.
        cachepath (str): Path to the cache directory.
        preset_image_size (str): Preset size of the images.
        custom_image_size_length (float): Custom length of the images in mm.
        sheet_size (str): Size of the sheet for the PDF.
        custom_sheet_width (float): Custom width of the sheet in mm.
        custom_sheet_length (float): Custom length of the sheet in mm.
        gutter_margin_size (float): Size of the gutter margin.
        dpi (int): Dots per inch for the output PDF.
        verbose (bool): Flag to enable verbose logging.
        process_nested_containers (bool): Flag to process nested containers in the TTS Saved Object.
        exclude_card_urls (bool): Flag to exclude card URLs from processing.
        exclude_card_backs (bool): Flag to exclude card backs from processing.
        generate_bleed (bool): Flag to generate bleed for the images.
        sharpen_text (bool): Flag to sharpen text in the images.
        draw_cut_lines (bool): Flag to draw cut lines on the images.
        split_double_and_single (bool): Flag to split double-sided and single-sided cards into separate PDFs.
        double_only (bool): Flag to include only double-sided cards.
        single_only (bool): Flag to include only single-sided cards.
        save_images (bool): Flag to save images to the output directory.
        skip_pdf_generation (bool): Flag to arrange images into a PDF.
        cut_lines_on_margin_only (bool): Flag to draw cut lines only on the margin.
        no_cut_lines_on_last_sheet (bool): Flag to avoid drawing cut lines on the last sheet.
        bleed_width (float): Width of the generated bleed.
        line_width (int): Width of the cut lines.

    Returns:
        None
    """
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO) if verbose else logger.setLevel(logging.WARNING)

    logger.debug(f"output_directory: {output_directory}")
    logger.debug(f"path: {path}")
    logger.debug(f"cachepath: {cachepath}")
    logger.debug(f"preset_image_size: {preset_image_size}")
    logger.debug(f"custom_image_size_length: {custom_image_size_length}")
    logger.debug(f"sheet_size: {sheet_size}")
    logger.debug(f"gutter_margin_size: {gutter_margin_size}")
    logger.debug(f"dpi: {dpi}")
    logger.debug(f"verbose: {verbose}")
    logger.debug(f"process_nested_containers: {process_nested_containers}")
    logger.debug(f"exclude_card_urls: {exclude_card_urls}")
    logger.debug(f"generate_bleed: {generate_bleed}")
    logger.debug(f"sharpen_text: {sharpen_text}")
    logger.debug(f"draw_cut_lines: {draw_cut_lines}")
    logger.debug(f"split_double_and_single: {split_double_and_single}")
    logger.debug(f"save_images: {save_images}")
    logger.debug(f"skip_pdf_generation: {skip_pdf_generation}")
    logger.debug(f"cut_lines_on_margin_only: {cut_lines_on_margin_only}")
    logger.debug(f"no_cut_lines_on_last_sheet: {no_cut_lines_on_last_sheet}")
    logger.debug(f"bleed_width: {bleed_width}")
    logger.debug(f"line_width: {line_width}")

    os.makedirs(output_directory, exist_ok=True)

    try:
        with open("image_blacklist.txt", "r") as file:
            blacklist = file.read().splitlines() if exclude_card_urls else []
    except FileNotFoundError:
        blacklist = []

    if os.path.isdir(path):
        logger.info("Loading images from directory")
        images = load_images(path)
        if not images:
            raise ImageFilesNotFoundError()
        logger.info(f"Successfully loaded {len(images)} images from directory")
    elif os.path.isfile(path):
        with open(path, "r") as file:
            save_object_data = json.load(file)
        logger.info("Loading images from URLs in TTS Saved Object")
        images = process_tts_object(
            save_object_data,
            process_nested_containers,
            blacklist,
            cachepath,
            exclude_card_backs,
        )
        if not images:
            raise CardsNotFoundError()
        logger.info(f"Successfully loaded {len(images)} images")
    else:
        images = []
        logger.error(f"Invalid path: {path}")

    if save_images:
        logger.info("Saving images")
        os.makedirs(f"{output_directory}/img", exist_ok=True)
        for idx, image in enumerate(images):
            for key, value in image.items():
                if value:
                    value.save(f"{output_directory}/img/card_{idx}_{key}.png")
        logger.info(f"Images saved to {output_directory}")

    def generate_pdf_wrapper(_images, filename):
        generate_pdf(
            _images,
            output_directory,
            sheet_size,
            image_length,
            dpi,
            logger,
            draw_cut_lines,
            generate_bleed,
            sharpen_text,
            gutter_margin_size,
            filename=filename,
            cut_lines_on_margin_only=cut_lines_on_margin_only,
            no_cut_lines_on_last_sheet=no_cut_lines_on_last_sheet,
            bleed_width=bleed_width,
            line_width=line_width,
        )

    if not skip_pdf_generation:
        custom_sheet_width_px_at_300dpi = int(custom_sheet_width / 25.4 * 300)
        custom_sheet_length_px_at_300dpi = int(custom_sheet_length / 25.4 * 300)
        sheet_size = (
            SHEET_SIZES[sheet_size]
            if custom_sheet_width == 0 or custom_sheet_length == 0
            else (custom_sheet_width_px_at_300dpi, custom_sheet_length_px_at_300dpi)
        )

        # Create a variable `image_size` and set it to the preset image size if any of the custom image sizes are 0
        image_length = (
            CARD_SIZES[preset_image_size][1] / 300 * 25.4
            if custom_image_size_length == 0
            else custom_image_size_length
        )
        logger.debug(f"image_length: {image_length}")

        # Remove keys with None values
        images = [{k: v for k, v in image.items() if v is not None} for image in images]

        if split_double_and_single:
            # if image dict has both face and back keys then it is a double-sided card
            double_sided_cards = [
                image for image in images if "face" in image and "back" in image
            ]
            # if image dict only has a face or a back key then it is a single-sided card
            single_sided_cards = [
                image for image in images if ("face" in image) ^ ("back" in image)
            ]

            # Extract all images into a single list
            double_sided_images = [
                image[key] for image in double_sided_cards for key in ["face", "back"]
            ]
            single_sided_images = [
                image[key]
                for image in single_sided_cards
                for key in ["face", "back"]
                if key in image
            ]

            logger.info(
                "Arranging images into separate PDFs for single and double sided cards"
            )

            if not double_only and not single_only:
                # Generate both single-sided and double-sided PDFs
                generate_pdf_wrapper(single_sided_images, "output_single.pdf")
                generate_pdf_wrapper(double_sided_images, "output_double.pdf")
            elif double_only:
                # Generate only double-sided PDF
                generate_pdf_wrapper(double_sided_images, "output_double.pdf")
            elif single_only:
                # Generate only single-sided PDF
                generate_pdf_wrapper(single_sided_images, "output_single.pdf")
        else:
            images_list = [
                image[key]
                for image in images
                for key in ["face", "back"]
                if key in image
            ]
            logger.info("Arranging images into PDF")
            generate_pdf_wrapper(images_list, "output.pdf")
