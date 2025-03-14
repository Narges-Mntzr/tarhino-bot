from balethon.objects import ReplyKeyboard
import config
from services.general import get_all_template_names, convert_english_to_persian_digits


before_register = ReplyKeyboard(
    ["ثبت‌نام"],
    ["راهنما"],
)

main_menu = ReplyKeyboard(
    ["شروع"],
    # TODO: ["فایل‌های من"],
    # TODO: ["پشتیبانی"],
    ["تنظیمات اکانت"],
)

setting_menu = ReplyKeyboard(
    ["فونت"],
    ["رنگ‌بندی"],
    ["بازگشت به منو"],
)

font_menu = ReplyKeyboard(
    ["Ray"],
    ["Vazirmatn"],
    ["بازگشت به منو"],
)

color_menu = ReplyKeyboard(
    ["رنگ اصلی"],
    ["رنگ فرعی"],
    ["رنگ متن"],
    ["بازگشت به منو"],
)

start_menu = ReplyKeyboard(
    ["عکس نوشت"],
    ["گنجینه تصاویر"],
    ["بازگشت به منو"],
)

return_menu = ReplyKeyboard(["بازگشت به منو"])

mode_selection_menu = ReplyKeyboard(
    ["تولید عکس‌نوشت تکی"],
    ["تولید عکس‌نوشت دسته‌ای"],
    ["بازگشت به منو"],
)

type_selection_menu = ReplyKeyboard(
    ["ساده"],
    ["کارت‌پستال"],
    ["دعوت‌نامه"],
    ["بازگشت به منو"],
)

type_selection_group_menu = ReplyKeyboard(
    ["کارت‌پستال"],
    ["دعوت‌نامه"],
    ["بازگشت به منو"],
)

places = ReplyKeyboard(*[[dept] for dept in config.PLACES], ["بازگشت به منو"])

sub_places = {
    key: ReplyKeyboard(*[[item] for item in values], ["بازگشت به منو"])
    for key, values in config.PLACES.items()
}

orientation_menu = ReplyKeyboard(
    ["افقی"],
    ["عمودی"],
    ["بازگشت به منو"],
)


def generate_template_keyboard(path):
    return ReplyKeyboard(
        *[[f"طرح {name}"] for name in get_all_template_names(path)], ["بازگشت به منو"]
    )


def generate_image_keyboard(n, prefix):
    return ReplyKeyboard(
        *[
            [f"{prefix} - عکس {convert_english_to_persian_digits(str(i + 1))}"]
            for i in range(n)
        ],
        ["بازگشت به منو"],
    )


default = ReplyKeyboard(["مقدار پیش‌فرض"])

default_title = ReplyKeyboard(
    ["تایید عنوان پیش‌فرض"],
    ["بازگشت به منو"],
)
