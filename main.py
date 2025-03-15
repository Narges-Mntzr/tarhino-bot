# NOTE: use balethon
# pip install Balethon

from balethon import Client, conditions
from balethon.objects import Message

import config
import texts
import keyboards
from handlers.register_handlers import register_handlers
from handlers.setting_handlers import setting_handlers
from handlers.poster_handlers import poster_handlers
from handlers.poster_handlers_group import poster_handlers_group
from handlers.image_places_handlers import image_places_handlers
from database import Database

# bot = Client(config.TOKEN, proxy="socks5://127.0.0.1:2080/")
bot = Client(config.TOKEN)


@bot.on_command()
async def start(*, message: Message):
    user = Database.load_user(message.author.id)

    if user.needs_registration():
        await message.reply(texts.needs_registration, keyboards.before_register)
        message.author.set_state("BEFORE_REG")
    else:
        await message.reply(texts.start, keyboards.main_menu)
        message.author.set_state("MAIN")


@bot.on_message(
    (conditions.at_state("MAIN") | conditions.at_state(None))
    & conditions.regex("^شروع$")
)
async def main1_state(message: Message):
    await message.reply(texts.start_message, keyboards.start_menu)
    message.author.set_state("START")


@bot.on_message(conditions.at_state("MAIN") & conditions.regex("^تنظیمات اکانت$"))
async def main2_state(message: Message):
    await message.reply(texts.setting_menu, keyboards.setting_menu)
    message.author.set_state("SETTING")


@bot.on_message(conditions.at_state("MAIN") & conditions.regex("^پشتیبانی$"))
async def main3_state(message: Message):
    await message.reply(texts.support)


@bot.on_message(conditions.at_state("START") & conditions.regex("^گنجینه تصاویر$"))
async def start_image_state(message: Message):
    await message.reply(texts.places, keyboards.places)
    message.author.set_state("PLACE")


@bot.on_message(conditions.regex("^بازگشت به منو$"))
async def setting3_state(message: Message):
    await message.reply(texts.main_menu, keyboards.main_menu)
    message.author.set_state("MAIN")


@bot.on_message(
    conditions.at_state(None) & ~conditions.regex("^(شروع|تنظیمات اکانت|پشتیبانی)$")
)
async def none_state(message: Message):
    await message.reply(texts.none_state, keyboards.main_menu)
    message.author.set_state("MAIN")


register_handlers(bot)
setting_handlers(bot)
poster_handlers(bot)
poster_handlers_group(bot)
image_places_handlers(bot)

bot.run()
