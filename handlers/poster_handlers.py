from balethon import conditions
from balethon.objects import Message

import config
import keyboards
import texts
from database import Database
from services.ai import get_title_with_ai
from services.general import (
    is_template_exist,
    download_photo_as_bytes,
    generate_template_grid,
    get_poster_type,
    define_text_color,
)
from services.visualize import process_poster, process_poster_without_image


def poster_handlers(bot):
    @bot.on_message(conditions.at_state("START") & conditions.regex("^عکس نوشت$"))
    async def start_poster_state(message: Message):
        await message.reply(
            texts.mode_selection, reply_markup=keyboards.mode_selection_menu
        )
        message.author.set_state("MODE-SELECTION")

    @bot.on_message(conditions.at_state("MODE-SELECTION") & conditions.regex("^تولید عکس‌نوشت تکی$"))
    async def mode_selection_state(message: Message):
        await message.reply(
            texts.type_selection, reply_markup=keyboards.type_selection_menu
        )
        message.author.set_state("TYPE-SELECTION")

    @bot.on_message(conditions.at_state("TYPE-SELECTION") & conditions.regex("^ساده"))
    async def type_selection_state1(message: Message):
        if not is_template_exist():
            await message.reply("هیچ طرحی موجود نیست.")
            return

        user = Database.load_user(message.author.id)

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = config.BASIC_TEMPLATE_PATH
        Database.save_poster(poster)

        template_grid = generate_template_grid(
            image_dir=config.BASIC_TEMPLATE_PATH, new_colors=[user.color1, user.color2]
        )
        await message.reply_photo(photo=template_grid)

        await message.reply(
            texts.template_selection, reply_markup=keyboards.generate_template_keyboard(config.BASIC_TEMPLATE_PATH)
        )
        message.author.set_state("TEMPLATE-SELECTION")

    @bot.on_message(conditions.at_state("TYPE-SELECTION") & conditions.regex("^کارت‌پستال"))
    async def type_selection_state2(message: Message):
        if not is_template_exist():
            await message.reply("هیچ طرحی موجود نیست.")
            return

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = config.POSTCARD_TEMPLATE_PATH
        Database.save_poster(poster)

        template_grid = generate_template_grid(image_dir=config.POSTCARD_TEMPLATE_PATH)
        await message.reply_photo(photo=template_grid)

        await message.reply(
            texts.template_selection, reply_markup=keyboards.generate_template_keyboard(config.POSTCARD_TEMPLATE_PATH)
        )
        message.author.set_state("TEMPLATE-SELECTION2")

    @bot.on_message(conditions.at_state("TYPE-SELECTION") & conditions.regex("^دعوت‌نامه"))
    async def type_selection_state3(message: Message):
        if not is_template_exist():
            await message.reply("هیچ طرحی موجود نیست.")
            return

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = config.INVITATION_TEMPLATE_PATH
        Database.save_poster(poster)

        template_grid = generate_template_grid(image_dir=config.INVITATION_TEMPLATE_PATH)
        await message.reply_photo(photo=template_grid)

        await message.reply(
            texts.template_selection, reply_markup=keyboards.generate_template_keyboard(config.INVITATION_TEMPLATE_PATH)
        )
        message.author.set_state("TEMPLATE-SELECTION2")    


    @bot.on_message(conditions.at_state("TEMPLATE-SELECTION2"))
    async def template_selection_state2(message: Message):
        template_name = message.text.split()[-1]

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = f'{poster.template}/{template_name}'
        Database.save_poster(poster)

        poster_type = get_poster_type(poster.template)
        await message.reply(texts.generate_heading2_message(poster_type))
        message.author.set_state("HEADING1")


    @bot.on_message(conditions.at_state("TEMPLATE-SELECTION"))
    async def template_selection_state(message: Message):
        template_name = message.text.split()[-1]
        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = f'{poster.template}/{template_name}'
        Database.save_poster(poster)

        await message.reply(texts.initial_image, reply_markup=keyboards.return_menu)
        message.author.set_state("INITIAL-IMAGE")

    @bot.on_message(conditions.at_state("INITIAL-IMAGE"))
    async def initial_image_state(message: Message):
        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.initial_image = message.photo[-1].id
        Database.save_poster(poster)

        poster_type = get_poster_type(poster.template)
        await message.reply(texts.generate_heading2_message(poster_type))
        # message.author.set_state("HEADING1-BASIC")
        message.author.set_state("HEADING1")

    @bot.on_message(conditions.at_state("HEADING1"))
    async def heading1_state1(message: Message):
        # if len(heading1.split()) > 20:
        #     await message.reply(texts.not_valid_length)
        #     return

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.message_text = message.text
        Database.save_poster(poster)

        poster_type = get_poster_type(poster.template)
        await message.reply(texts.generate_heading1_message(poster_type))
        message.author.set_state("FINAL-STATE")

    @bot.on_message(conditions.at_state("HEADING1-BASIC"))
    async def heading1_state2(message: Message):
        ai_title = get_title_with_ai(message.text)

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.message_text = message.text
        poster.title = ai_title
        Database.save_poster(poster)

        await message.reply(
            texts.heading1_message_with_default.format(title=ai_title),
            reply_markup=keyboards.default_title,
        )
        message.author.set_state("FINAL-STATE")

    @bot.on_message(conditions.at_state("FINAL-STATE"))
    async def poster_generation_state(message: Message):
        if message.text != "تایید عنوان پیش‌فرض":
            heading2 = message.text
            # if len(heading2.split()) > 10:
            #     await message.reply(texts.not_valid_length)
            #     return
            poster = Database.load_posters_by_user(user_id=message.author.id)
            poster.title = heading2

        if poster.initial_image:
            photo_file = await message.client.get_file(poster.initial_image)
            photo_bytes = await download_photo_as_bytes(photo_file.path)

        poster.text_color = define_text_color(poster.template)
        try:
            if get_poster_type(poster.template) == "basic":
                final_bytes = process_poster(poster, photo_bytes)
            else:
                final_bytes = process_poster_without_image(poster)

            uploaded_photo = await message.reply_photo(final_bytes)
            await message.reply_document(
                final_bytes, texts.completed_poster, reply_markup=keyboards.main_menu
            )
            message.author.set_state("MAIN")

            poster.output_image = uploaded_photo.photo[-1].id
            Database.save_poster(poster)
        except Exception as e:
            await message.reply(texts.error.format(error_msg=str(e)))
