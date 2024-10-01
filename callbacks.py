import json
import logging
import os
import re
from urllib.request import urlopen

from PIL import Image

from pdf_generation import generate_pdf


# Define preset card sizes in pixels at 300dpi
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


def download_image(url: str, blacklist: list[str], cache_folder: str) -> Image:
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


def process_deck(deck: dict, blacklist: list, cachepath: str) -> list[dict]:
    contained_objects = deck.get("ContainedObjects", {})
    images = []
    for card in contained_objects:
        card_images = process_card(card, blacklist, cachepath)
        images.append(card_images)
    logger.info(f"Processed deck containing {len(images)} cards")
    return images


def process_card(card: dict, blacklist: list, cachepath: str) -> dict:
    nickname = card.get("Nickname", "")
    card_id = card.get("CardID", "")
    custom_deck = card.get("CustomDeck", {})
    custom_deck_key = list(custom_deck)[0]
    face_url = custom_deck[custom_deck_key].get("FaceURL", "")
    back_url = custom_deck[custom_deck_key].get("BackURL", "")
    num_width = custom_deck[custom_deck_key].get("NumWidth", 1)
    num_height = custom_deck[custom_deck_key].get("NumHeight", 1)

    # Download and split the sprite sheet for the deck
    image = {}
    if face_url:
        sprite_sheet = download_image(face_url, blacklist, cachepath)
        if sprite_sheet:
            card_face = crop_from_sprite_sheet(
                sprite_sheet, num_width, num_height, card_id
            )
            image["face"] = card_face

    if back_url:
        card_back = download_image(back_url, blacklist, cachepath)
        if card_back:
            image["back"] = card_back

    logger.info(f"Processed card: {nickname}")
    return image


def process_container(
    container, process_nested_containers, blacklist, output_directory, cachepath: str
):
    object_states = container.get("ObjectStates", [])

    images = []
    for obj in object_states:
        obj_name = obj.get("Name", "")
        if obj_name == "Deck":  # Process deck
            logger.info(f"Processing deck: {obj.get('Nickname', 'Unknown Deck')}")
            images.extend(process_deck(obj, blacklist, cachepath))
        elif obj_name == "Card":  # Process single card
            logger.info(f"Processing card: {obj.get('Nickname', 'Unknown Card')}")
            images.append(process_card(obj, blacklist))
        elif obj_name == "Bag":  # Process container (Bag)
            logger.info(
                f"Processing container: {obj.get('Nickname', 'Unknown Container')}"
            )
            # Create a subfolder for this container
            sub_dir = os.path.join(output_directory, f"container_{obj['GUID']}")
            os.makedirs(sub_dir, exist_ok=True)
            process_container(obj, sub_dir, blacklist)
        else:
            logger.warning(f"Unknown object type: {obj_name}")
        return images


def load_images(output_directory: str) -> list[Image.Image]:
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
        images.append(image)
    return images


def start_script(
    filepath: str,
    cachepath: str,
    preset_image_size: tuple,
    custom_image_size_width: int,
    custom_image_size_length: int,
    sheet_size: tuple,
    gutter_margin_size: float,
    dpi: int,
    verbose: bool,
    process_nested_containers: bool,
    exclude_card_urls: bool,
    generate_bleed: bool,
    sharpen_text: bool,
    draw_cut_lines: bool,
    split_face_and_back: bool,
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
    logger.debug(f"gutter_margin_size: {gutter_margin_size}")
    logger.debug(f"dpi: {dpi}")
    logger.debug(f"verbose: {verbose}")
    logger.debug(f"process_nested_containers: {process_nested_containers}")
    logger.debug(f"exclude_card_urls: {exclude_card_urls}")
    logger.debug(f"generate_bleed: {generate_bleed}")
    logger.debug(f"sharpen_text: {sharpen_text}")
    logger.debug(f"draw_cut_lines: {draw_cut_lines}")
    logger.debug(f"split_face_and_back: {split_face_and_back}")
    logger.debug(f"save_images: {save_images}")
    logger.debug(f"load_images_from_directory: {load_images_from_directory}")
    logger.debug(f"arrange_into_pdf: {arrange_into_pdf}")

    output_directory = "./output"
    os.makedirs(output_directory, exist_ok=True)

    with open("image_blacklist.txt", "r") as file:
        blacklist = file.read().splitlines() if exclude_card_urls else []

    if load_images_from_directory:
        logger.info("Loading images from directory")
        if split_face_and_back:
            face_images = load_images(f"{output_directory}/img/face_images")
            logger.info(
                f"Successfully loaded {len(face_images)} face images from directory"
            )
            back_images = load_images(f"{output_directory}/img/back_images")
            logger.info(
                f"Successfully loaded {len(back_images)} back images from directory"
            )
        else:
            images = load_images(f"{output_directory}/img")
            logger.info(f"Successfully loaded {len(images)} images from directory")
    else:
        with open(filepath, "r") as file:
            save_object_data = json.load(file)

        logger.info("Loading images from URLs in TTS Saved Object")
        images = process_container(
            save_object_data,
            process_nested_containers,
            blacklist,
            output_directory,
            cachepath,
        )
        logger.info(f"Successfully loaded {len(images)} images")
        if split_face_and_back:
            face_images = [image["face"] for image in images if "face" in image]
            back_images = [image["back"] for image in images if "back" in image]
            logger.info(f"Successfully separated {len(face_images)} face images")
            logger.info(f"Successfully separated {len(back_images)} back images")

    if save_images:
        logger.info("Saving images")
        if split_face_and_back:
            os.makedirs(f"{output_directory}/img/face_images", exist_ok=True)
            os.makedirs(f"{output_directory}/img/back_images", exist_ok=True)

            for idx, image in enumerate(face_images):
                image.save(f"{output_directory}/img/face_images/card_{idx}_face.png")
            for idx, image in enumerate(back_images):
                image.save(f"{output_directory}/img/back_images/card_{idx}_back.png")
        else:
            os.makedirs(f"{output_directory}/img", exist_ok=True)

            for idx, image in enumerate(images):
                for key, value in image.items():
                    value.save(f"{output_directory}/img/card_{idx}_{key}.png")
        logger.info(f"Images saved to {output_directory}")

    if arrange_into_pdf:
        sheet_size = SHEET_SIZES[sheet_size]
        # Create a variable `image_size` and set it to the preset image size if any of the custom image sizes are 0
        image_size = (
            CARD_SIZES[preset_image_size]
            if custom_image_size_width == 0 or custom_image_size_length == 0
            else (custom_image_size_width, custom_image_size_length)
        )
        image_length = image_size[1]
        logger.debug(f"image_size: {image_size}")

        if split_face_and_back:
            logger.info("Arranging images into PDF with separate face and back images")
            for i, images in enumerate([face_images, back_images]):
                generate_pdf(
                    images,
                    output_directory,
                    sheet_size,
                    image_length,
                    dpi,
                    logger,
                    draw_cut_lines,
                    generate_bleed,
                    sharpen_text,
                    gutter_margin_size,
                    filename=f"output_face.pdf" if i == 0 else "output_back.pdf",
                )
        else:
            logger.info("Arranging images into PDF")
            generate_pdf(
                images,
                output_directory,
                sheet_size,
                image_length,
                dpi,
                logger,
                draw_cut_lines,
                generate_bleed,
                sharpen_text,
                gutter_margin_size,
                filename="output.pdf",
            )
