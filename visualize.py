import os
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

import config


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_bgr(hex_color):
    """Convert hex color to BGR tuple for OpenCV."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (4, 2, 0))  # Convert to BGR


def read_colors_from_file(file_path):
    """Read hex colors from a text file."""
    with open(file_path, "r") as file:
        colors = [line.strip() for line in file.readlines()]
    return colors


def replace_colors(image_path, old_colors, new_colors):
    """Replace two specified colors in an image."""
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or cannot be loaded.")

    # Convert hex colors to BGR
    old_bgr = [hex_to_bgr(color) for color in old_colors]
    new_bgr = [hex_to_bgr(color) for color in new_colors]

    # Create masks and replace colors
    for i in range(2):
        lower_bound = np.array(old_bgr[i]) - 20  # Allow slight variations
        upper_bound = np.array(old_bgr[i]) + 20
        mask = cv2.inRange(image, lower_bound, upper_bound)
        image[mask > 0] = new_bgr[i]

    return image


def read_coordinates(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    boxes = []
    for line in lines:
        coords = list(map(int, line.split()[:4]))
        boxes.append([tuple(coords[:2]), tuple(coords[2:])])  # (x1, y1), (x2, y2)

    return boxes


def add_elements(
    image, text_boxes, text_values, text_color, is_persian, font_path, bold_font_path
):
    output_image = image.copy()

    # Using PIL to add text with custom fonts
    pil_image = Image.fromarray(output_image)
    draw = ImageDraw.Draw(pil_image)

    for i, (text, box) in enumerate(zip(text_values, text_boxes)):
        x1, y2 = box[0]
        x2, y1 = box[1]

        font_size_small = 30
        font_size_large = 50

        font_size = font_size_small if i == 0 else font_size_large
        new_font_path = font_path if i == 0 else bold_font_path
        font = ImageFont.truetype(new_font_path, font_size)

        # Get text bounding box
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if is_persian:
            text_x = x2 - text_width - 10
        else:
            text_x = x1 + 10

        # For the second box, handle long text by splitting it into two lines
        if i == 1:
            # Calculate the maximum width available for text within the box
            max_text_width = x2 - x1 - 20  # Subtract some padding

            # Split the text into lines based on the available width
            lines = []
            current_line = ""
            for word in text.split():
                word_bbox = font.getbbox(word)
                word_width = word_bbox[2] - word_bbox[0]
                if len(current_line) > 0:
                    current_line_bbox = font.getbbox(current_line + " " + word)
                    current_line_width = current_line_bbox[2] - current_line_bbox[0]
                else:
                    current_line_width = word_width

                if current_line_width > max_text_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    if len(current_line) > 0:
                        current_line += " "
                    current_line += word

            if len(current_line) > 0:
                lines.append(current_line)

            # Calculate the y position for each line
            text_y = y1 + 10  # Start from the top with some padding
            for line in lines:
                line_bbox = font.getbbox(line)
                line_height = line_bbox[3] - line_bbox[1]
                line_width = line_bbox[2] - line_bbox[0]

                # Center the text within the box
                line_x = x1 + (x2 - x1 - line_width) // 2

                draw.text((line_x, text_y), line, fill=text_color[i][::-1], font=font)
                text_y += (
                    line_height + 5
                )  # Move down for the next line with some spacing

        else:
            # For other boxes, handle text as before
            text_y = y1 + (y2 - y1 + text_height) // 2
            draw.text((text_x, text_y), text, fill=text_color[i][::-1], font=font)

    output_image = np.array(pil_image)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    _, imgencode = cv2.imencode(".jpg", output_image, encode_param)
    image_bytes = imgencode.tobytes()
    return image_bytes


def process_poster(poster, photo_bytes=None, is_persian=True):
    # Validate required attributes

    # Construct paths dynamically
    template_folder = poster.template
    template_image_path = os.path.join(template_folder, "bg.png")
    coordinates_path = os.path.join(template_folder, "coordinates.txt")
    color_path = os.path.join(template_folder, "colors.txt")

    # Validate file existence
    if not os.path.exists(template_image_path):
        raise FileNotFoundError(
            f"Template background not found at {template_image_path}"
        )

    if not os.path.exists(coordinates_path):
        raise FileNotFoundError(f"Coordinates file not found at {coordinates_path}")

    if not os.path.exists(color_path):
        raise FileNotFoundError(f"Colors file not found at {color_path}")

    # Convert bytes to an OpenCV image
    np_arr = np.frombuffer(photo_bytes, np.uint8)
    initial_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Read coordinate boxes
    boxes = read_coordinates(coordinates_path)
    if len(boxes) < 3:
        raise ValueError(
            "Invalid coordinate file! Ensure it has at least 3 bounding boxes."
        )

    image_box, text_box_1, text_box_2 = boxes[0], boxes[1], boxes[2]

    # Load font file dynamically
    font_path = os.path.join(config.FONT_PATH, f"{poster.font}.ttf")
    bold_font_path = os.path.join(config.FONT_PATH, f"{poster.font}-Bold.ttf")
    if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
        raise FileNotFoundError(f"Font file not found at {font_path}")

    # Replace colors in the template image
    old_colors = read_colors_from_file(color_path)
    modified_image = replace_colors(
        template_image_path, old_colors, [poster.color1, poster.color2]
    )

    # Insert the user-uploaded image into the template at `image_box`
    x1, y2 = image_box[0]
    x2, y1 = image_box[1]
    target_width = x2 - x1
    target_height = y2 - y1

    if target_width > 0 and target_height > 0:
        user_image_resized = cv2.resize(initial_image, (target_width, target_height))
        modified_image[y1:y2, x1:x2] = user_image_resized
    else:
        raise ValueError("Invalid image box dimensions!")

    # Add text elements after inserting the user image
    final_image = add_elements(
        image=modified_image,
        text_boxes=[text_box_1, text_box_2],
        text_values=[poster.title, poster.message_text],
        text_color=[hex_to_rgb(poster.color2), hex_to_rgb(poster.text_color)],
        is_persian=is_persian,
        font_path=font_path,
        bold_font_path=bold_font_path,
    )

    return final_image

def process_poster_without_image(poster, is_persian=True):
    # Validate required attributes

    # Construct paths dynamically
    template_folder = poster.template
    template_image_path = os.path.join(template_folder, "bg.png")
    coordinates_path = os.path.join(template_folder, "coordinates.txt")

    # Validate file existence
    if not os.path.exists(template_image_path):
        raise FileNotFoundError(f"Template background not found at {template_image_path}")

    if not os.path.exists(coordinates_path):
        raise FileNotFoundError(f"Coordinates file not found at {coordinates_path}")

    # Read coordinate boxes
    boxes = read_coordinates(coordinates_path)
    if len(boxes) < 2:  # Only text boxes are needed now
        raise ValueError("Invalid coordinate file! Ensure it has at least 2 bounding boxes.")

    text_box_1, text_box_2 = boxes[0], boxes[1]

    # Load font file dynamically
    font_path = os.path.join(config.FONT_PATH, f"{poster.font}.ttf")
    bold_font_path = os.path.join(config.FONT_PATH, f"{poster.font}-Bold.ttf")

    if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
        raise FileNotFoundError(f"Font file not found at {font_path}")

    # Load the template image as it is (no color replacement)
    modified_image = cv2.imread(template_image_path, cv2.IMREAD_COLOR)

    # Add text elements
    final_image = add_elements(
        image=modified_image,
        text_boxes=[text_box_1, text_box_2],
        text_values=[poster.title, poster.message_text],
        text_color=[hex_to_rgb(poster.text_color), hex_to_rgb(poster.text_color)],  # Use the same text color
        is_persian=is_persian,
        font_path=font_path,
        bold_font_path=bold_font_path,
    )

    return final_image