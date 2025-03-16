from balethon import conditions
from balethon.objects import Message

import texts
import keyboards
from database import Database
from services.general import (
    generate_color_palette,
    is_valid_hex_color,
)


def setting_handlers(bot):
    @bot.on_message(conditions.at_state("SETTING") & conditions.regex("^فونت$"))
    async def setting1_state(message: Message):
        user = Database.load_user(message.author.id)
        await message.reply(texts.font_menu.format(font=user.font), keyboards.font_menu)
        message.author.set_state("FONT")

    @bot.on_message(conditions.at_state("SETTING") & conditions.regex("^رنگ‌بندی$"))
    async def setting2_state(message: Message):
        user = Database.load_user(message.author.id)
        await message.reply(texts.color_menu, keyboards.color_menu)

        pallete = generate_color_palette(user.color1, user.color2, user.color_text)
        await message.reply_photo(photo=pallete)
        message.author.set_state("COLOR")

    @bot.on_message(conditions.at_state("FONT") & conditions.regex("^(Vazirmatn|Ray)$"))
    async def font1_state(message: Message):
        user = Database.load_user(message.author.id)
        user.font = message.text
        Database.save_user(user)
        await message.reply(texts.ok_status, keyboards.main_menu)
        message.author.set_state("MAIN")

    @bot.on_message(
        (conditions.at_state("FONT") | conditions.at_state("COLOR"))
        & conditions.regex("^بازگشت به مرحله قبل$")
    )
    async def return_setting_state(message: Message):
        await message.reply(texts.setting_menu, keyboards.setting_menu)
        message.author.set_state("SETTING")

    @bot.on_message(
        conditions.at_state("COLOR") & conditions.regex("^(رنگ اصلی|رنگ فرعی|رنگ متن)$")
    )
    async def color_color1_state(message: Message):
        await message.reply(
            texts.give_color.format(color_name=message.text), keyboards.return_menu
        )

        if message.text == "رنگ اصلی":
            message.author.set_state("COLOR1")
        elif message.text == "رنگ فرعی":
            message.author.set_state("COLOR2")
        elif message.text == "رنگ متن":
            message.author.set_state("COLOR_TEXT")

    @bot.on_message(conditions.at_state("COLOR1"))
    async def color1_state(message: Message):
        user = Database.load_user(message.author.id)

        if message.text == "بازگشت به مرحله قبل":
            await message.reply(texts.color_menu, keyboards.color_menu)

            pallete = generate_color_palette(user.color1, user.color2, user.color_text)
            await message.reply_photo(photo=pallete)
            message.author.set_state("COLOR")

        if not is_valid_hex_color(message.text):
            await message.reply(texts.invalid_value)
            return

        user.color1 = message.text
        Database.save_user(user)

        await message.reply(texts.ok_status, keyboards.main_menu)

        pallete = generate_color_palette(user.color1, user.color2, user.color_text)
        await message.reply_photo(photo=pallete)

        message.author.set_state("MAIN")

    @bot.on_message(conditions.at_state("COLOR2"))
    async def color2_state(message: Message):
        user = Database.load_user(message.author.id)

        if message.text == "بازگشت به مرحله قبل":
            await message.reply(texts.color_menu, keyboards.color_menu)

            pallete = generate_color_palette(user.color1, user.color2, user.color_text)
            await message.reply_photo(photo=pallete)
            message.author.set_state("COLOR")

        if not is_valid_hex_color(message.text):
            await message.reply(texts.invalid_value)
            return

        user.color2 = message.text
        Database.save_user(user)

        await message.reply(texts.ok_status, keyboards.main_menu)

        pallete = generate_color_palette(user.color1, user.color2, user.color_text)
        await message.reply_photo(photo=pallete)

        message.author.set_state("MAIN")

    @bot.on_message(conditions.at_state("COLOR_TEXT"))
    async def color_text_state(message: Message):
        user = Database.load_user(message.author.id)

        if message.text == "بازگشت به مرحله قبل":
            await message.reply(texts.color_menu, keyboards.color_menu)

            pallete = generate_color_palette(user.color1, user.color2, user.color_text)
            await message.reply_photo(photo=pallete)
            message.author.set_state("COLOR")

        if not is_valid_hex_color(message.text):
            await message.reply(texts.invalid_value)
            return

        user.color_text = message.text
        Database.save_user(user)

        await message.reply(texts.ok_status, keyboards.main_menu)

        pallete = generate_color_palette(user.color1, user.color2, user.color_text)
        await message.reply_photo(photo=pallete)

        message.author.set_state("MAIN")
