from balethon import conditions
from balethon.objects import Message, ReplyKeyboardRemove

import texts
import keyboards
from database import Database
from services import (
    convert_persian_to_english_digits,
    is_valid_phone_number,
)


def register_handlers(bot):
    @bot.on_message(conditions.at_state("BEFORE_REG") & conditions.regex("^راهنما$"))
    async def before_reg1_state(message: Message):
        await message.reply(texts.help_reg)

    @bot.on_message(conditions.at_state("BEFORE_REG") & conditions.regex("^ثبت‌نام$"))
    async def before_reg2_state(message: Message):
        await message.reply(texts.give_name, ReplyKeyboardRemove())
        message.author.set_state("NAME")

    @bot.on_message(conditions.at_state("NAME"))
    async def name_state(message: Message):
        user = Database.load_user(message.author.id)
        user.name = message.text
        Database.save_user(user)

        if user.phone_number is None:
            await message.reply(texts.give_phone_number)
            message.author.set_state("PHONE_NUMBER")
        else:
            await message.reply(texts.main_menu, keyboards.main_menu)
            message.author.set_state("MAIN")

    @bot.on_message(conditions.at_state("PHONE_NUMBER"))
    async def phone_number_state(message: Message):
        normalized_number = convert_persian_to_english_digits(message.text)

        if not is_valid_phone_number(normalized_number):
            await message.reply(texts.invalid_value)
            return

        user = Database.load_user(message.author.id)
        user.phone_number = normalized_number
        Database.save_user(user)

        await message.reply(texts.main_menu, keyboards.main_menu)
        message.author.set_state("MAIN")
