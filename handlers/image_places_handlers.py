from balethon import conditions
from balethon.objects import Message

import config
import texts
import keyboards
from services.general import (
    generate_image_grid,
    convert_persian_to_english_digits,
    image_to_bytes,
)


def image_places_handlers(bot):
    @bot.on_message(conditions.at_state("PLACE"))
    async def place_state(message: Message):
        if message.text == "بازگشت به مرحله قبل":
            await message.reply(texts.start_message, keyboards.start_menu)
            message.author.set_state("START")
            return

        await message.reply(texts.places, keyboards.sub_places[message.text])
        message.author.set_state("SUB_PLACES")

    @bot.on_message(conditions.at_state("SUB_PLACES"))
    async def sub_place_state(message: Message):
        if message.text == "بازگشت به مرحله قبل":
            await message.reply(texts.places, keyboards.places)
            message.author.set_state("PLACE")
            return

        place_path = config.PLACES_PATH_MAPPING.get(message.text)
        if not place_path:
            await message.reply(texts.invalid_value)
            return

        grid, image_cnt = generate_image_grid(f"./images/{place_path}")
        await message.reply_photo(photo=grid)

        await message.reply(
            texts.places, keyboards.generate_image_keyboard(image_cnt, message.text)
        )
        message.author.set_state("IMAGE_SUB_PLACES")

    @bot.on_message(conditions.at_state("IMAGE_SUB_PLACES"))
    async def image_sub_place_state(message: Message):
        if message.text.startswith("بازگشت به دسته"):
            rest_of_string = message.text[len("بازگشت به دسته "):]
            await message.reply(texts.places, keyboards.sub_places[rest_of_string])
            message.author.set_state("SUB_PLACES")
            return

        place_name, img_name = message.text.split("-")
        place_path = config.PLACES_PATH_MAPPING.get(place_name[:-1])
        english_image = convert_persian_to_english_digits(img_name[1:])
        try:
            img_number = int(english_image.split()[-1])
        except ValueError:
            await message.reply(texts.invalid_value)
            return

        image = image_to_bytes(f"./images/{place_path}/{img_number}.jpg")
        await message.reply_photo(photo=image, reply_markup=keyboards.main_menu)
        message.author.set_state("MAIN")
