from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.ERROR)

TEMPLATE_PATH = "./templates/"
BASIC_TEMPLATE_PATH = f'{TEMPLATE_PATH}/basic'
POSTCARD_TEMPLATE_PATH = f'{TEMPLATE_PATH}/postcard'
INVITATION_TEMPLATE_PATH = f'{TEMPLATE_PATH}/postcard'

FONT_PATH = "./fonts"

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")

PLACES = {
    "کارت تبریک": [
        "تبریک تولد",
        "تبریک عروسی",
    ],
    "بناهای تاریخی و مذهبی": [
        "حرم امام‌رضا(ع)",
        "تخت‌جمشید",
        "چهل‌ستون",
    ],
    "ورزشی": [
        "فوتبال",
        "والیبال",
        "ورزشی",
    ],
    "طبیعت": [
        "پارک‌‌ها",
        "سواحل",
    ],
    "سایر": [
        "انتزاعی",
    ],
}

PLACES_PATH_MAPPING = {
    "تبریک تولد": "birthday",
    "تبریک عروسی": "wedding",
    "حرم امام‌رضا(ع)": "emam_reze_shrine",
    "تخت‌جمشید": "takht_jamshid",
    "چهل‌ستون": "40soton",
    "فوتبال": "football",
    "والیبال": "volleyball",
    "ورزشی": "sport",
    "پارک‌‌ها": "park",
    "سواحل": "beach",
    "انتزاعی": "abstract",
}
