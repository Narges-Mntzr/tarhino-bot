from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.ERROR)

TEMPLATE_PATH = "./templates"
FONT_PATH = "./fonts"

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")

PLACES = {
    "پارک‌ها": [
        "پارک مشتاق",
        "پارک ناژوان",
    ],
    "بنا و آثار تاریخی": [
        "چهل‌ستون",
    ],
}

PLACES_PATH_MAPPING = {
    "پارک مشتاق": "moshtagh",
    "پارک ناژوان": "nazhvan",
    "چهل‌ستون": "40soton",
}
