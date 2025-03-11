import config
import cv2
import io
import os
import re
import requests
from PIL import Image, ImageDraw, ImageFont

from visualize import replace_colors, read_colors_from_file


def convert_persian_to_english_digits(text: str) -> str:
    # Mapping of Persian to English digits
    persian_to_english = {
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
    }

    # Replace Persian digits with English digits
    return "".join(persian_to_english.get(char, char) for char in text)


def convert_english_to_persian_digits(text: str) -> str:
    # Mapping of English to Persian digits
    english_to_persian = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }

    # Replace Persian digits with English digits
    return "".join(english_to_persian.get(char, char) for char in text)


def is_valid_phone_number(phone_number: str) -> bool:
    # Regex for a valid phone number format: starts with 0 and has exactly 11 digits
    pattern = re.compile(r"^09\d{9}$")  # Example: 09131234567
    return bool(pattern.match(phone_number))


def generate_color_palette(color1, color2, color_text):
    """
    Generates an image with three labeled squares for the given colors, including Persian text.
    """
    img_size = (300, 100)
    img = Image.new("RGB", img_size, "white")
    draw = ImageDraw.Draw(img)

    # Define square dimensions
    square_width = img_size[0] // 3
    square_height = img_size[1]

    colors = [color1, color2, color_text]
    labels = ["رنگ اصلی", "رنگ فرعی", "رنگ متن"]

    # Load a Persian-supporting font (adjust the font path as needed)
    try:
        font = ImageFont.truetype(f"{config.FONT_PATH}/Vazirmatn.ttf", size=15)
    except IOError:
        font = ImageFont.load_default()

    # Draw squares and labels
    for i, (color, label) in enumerate(zip(colors, labels)):
        x0 = i * square_width
        x1 = x0 + square_width
        draw.rectangle([x0, 0, x1, square_height], fill=color)

        text_x = x0 + 15
        text_y = square_height // 2 - 10
        draw.text((text_x, text_y), label, font=font, fill="black")

    # Save image to a BytesIO buffer
    image_bytes = io.BytesIO()
    img.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes.getvalue()


def is_valid_hex_color(hex_color: str):
    if not hex_color:
        return False

    hex_color = hex_color.lstrip("#")

    if len(hex_color) != 6 or any(c not in "0123456789ABCDEFabcdef" for c in hex_color):
        return False

    return True


def get_all_template_names(path):
    templates = [
        folder_name
        for folder_name in os.listdir(path)
        if os.path.isdir(os.path.join(path, folder_name))
    ]

    templates.sort()
    return templates


def is_template_exist() -> bool:
    if (
        os.path.exists(config.TEMPLATE_PATH)
        and os.path.getsize(config.TEMPLATE_PATH) > 0
    ):
        return True

    return False


def generate_image_grid(image_dir, max_images_per_page=8, columns=2):
    image_files = [
        f
        for f in os.listdir(image_dir)
        if f.lower().endswith(("png", "jpg", "jpeg", "gif", "bmp"))
    ]
    image_files.sort()

    image_size = (150, 150)
    padding = 10

    try:
        font = ImageFont.truetype(f"{config.FONT_PATH}/Vazirmatn.ttf", size=15)
    except IOError:
        font = ImageFont.load_default()

    rows_needed = (len(image_files) + columns - 1) // columns

    grid_width = columns * (image_size[0] + padding) + padding
    grid_height = rows_needed * (image_size[1] + padding) + padding

    grid_image = Image.new("RGBA", (grid_width, grid_height), (255, 255, 255, 255))

    draw = ImageDraw.Draw(grid_image)

    for idx in range(max_images_per_page):
        row = idx // columns
        col = idx % columns
        x_offset = col * (image_size[0] + padding) + padding
        y_offset = row * (image_size[1] + padding) + padding

        if idx < len(image_files):
            image_file = image_files[idx]

            img = Image.open(os.path.join(image_dir, image_file))
            img = img.resize(image_size)

            img.putalpha(200)

            grid_image.paste(img, (x_offset, y_offset), img)

            text = f"عکس {convert_english_to_persian_digits(str(idx + 1))}"

            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            text_x = x_offset + (image_size[0] - text_width) // 2
            text_y = y_offset + (image_size[1] - text_height) // 2

            draw.text((text_x, text_y), text, font=font, fill="black")

        else:
            white_square = Image.new("RGBA", image_size, (255, 255, 255, 255))
            grid_image.paste(white_square, (x_offset, y_offset))

    image_bytes = io.BytesIO()
    grid_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes.getvalue(), len(image_files)


def generate_template_grid(image_dir, new_colors=None, max_images_per_page=8, columns=2):
    image_files = [
        f for f in os.listdir(image_dir) if os.path.isdir(os.path.join(image_dir, f))
    ]
    image_files.sort()

    image_size = (150, 150)
    padding = 10

    try:
        font = ImageFont.truetype(f"{config.FONT_PATH}/Vazirmatn.ttf", size=15)
    except IOError:
        font = ImageFont.load_default()

    rows_needed = (len(image_files) + columns - 1) // columns

    grid_width = columns * (image_size[0] + padding) + padding
    grid_height = rows_needed * (image_size[1] + padding) + padding

    grid_image = Image.new("RGBA", (grid_width, grid_height), (255, 255, 255, 255))

    draw = ImageDraw.Draw(grid_image)

    for idx in range(max_images_per_page):
        row = idx // columns
        col = idx % columns
        x_offset = col * (image_size[0] + padding) + padding
        y_offset = row * (image_size[1] + padding) + padding

        if idx < len(image_files):
            image_file = image_files[idx]

            template_image_path = os.path.join(image_dir, f"{image_file}/bg.png")
            if new_colors:
                color_path = os.path.join(image_dir, f"{image_file}/colors.txt")
                old_colors = read_colors_from_file(color_path)
                modified_image = replace_colors(template_image_path, old_colors, new_colors)

                img = Image.fromarray(cv2.cvtColor(modified_image, cv2.COLOR_BGR2RGB))
            else:
                # Load the original image if new_colors is None
                img = Image.open(template_image_path).convert("RGB")

            img = img.resize(image_size)

            img.putalpha(255)

            grid_image.paste(img, (x_offset, y_offset), img)

            text = f"طرح {convert_english_to_persian_digits(str(idx + 1))}"

            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            text_x = x_offset + (image_size[0] - text_width) // 2
            text_y = y_offset + (image_size[1] - text_height) // 2

            draw.text((text_x, text_y), text, font=font, fill="white")

        else:
            white_square = Image.new("RGBA", image_size, (255, 255, 255, 255))
            grid_image.paste(white_square, (x_offset, y_offset))

    image_bytes = io.BytesIO()
    grid_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes.getvalue()


def image_to_bytes(image_path):
    with Image.open(image_path) as grid_image:
        image_bytes = io.BytesIO()

        grid_image.save(image_bytes, format="PNG")

        image_bytes.seek(0)

        return image_bytes.getvalue()


async def download_photo_as_bytes(photo_file_path):
    photo_url = f"https://tapi.bale.ai/file/bot{config.TOKEN}/{photo_file_path}"
    response = requests.get(photo_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(
            f"Failed to download photo: {response.status_code} - {response.text}"
        )


def get_full_name(first_name: str = "", last_name: str = "") -> str:
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name or last_name:
        return first_name or last_name
    return ""
