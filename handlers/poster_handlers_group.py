from balethon import conditions
from balethon.objects import Message

import config
import keyboards
import texts
from database import Database
from services.general import (
    define_text_color,
    generate_template_grid,
    get_poster_type,
    is_template_exist,
)
from services.visualize import process_poster_without_image
from validator import validate_text, validate_title


def poster_handlers_group(bot):
    @bot.on_message(
        conditions.at_state("MODE-SELECTION")
        & conditions.regex("^تولید عکس‌نوشت دسته‌ای$")
    )
    async def mode_selection_state(message: Message):
        await message.reply(
            texts.type_selection, reply_markup=keyboards.type_selection_group_menu
        )
        message.author.set_state("TYPE-SELECTION-GROUP")

    @bot.on_message(
        conditions.at_state("TYPE-SELECTION-GROUP")
        & conditions.regex("^بازگشت به مرحله قبل")
    )
    async def type_selection_state1(message: Message):
        await message.reply(
            texts.mode_selection, reply_markup=keyboards.mode_selection_menu
        )
        message.author.set_state("MODE-SELECTION")

    @bot.on_message(
        conditions.at_state("TYPE-SELECTION-GROUP") & conditions.regex("^کارت‌پستال")
    )
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
            texts.template_selection,
            reply_markup=keyboards.generate_template_keyboard(
                config.POSTCARD_TEMPLATE_PATH
            ),
        )
        message.author.set_state("TEMPLATE-SELECTION2-GROUP")

    @bot.on_message(
        conditions.at_state("TYPE-SELECTION-GROUP") & conditions.regex("^دعوت‌نامه")
    )
    async def type_selection_state3(message: Message):
        if not is_template_exist():
            await message.reply("هیچ طرحی موجود نیست.")
            return

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = config.INVITATION_TEMPLATE_PATH
        Database.save_poster(poster)

        template_grid = generate_template_grid(
            image_dir=config.INVITATION_TEMPLATE_PATH
        )
        await message.reply_photo(photo=template_grid)

        await message.reply(
            texts.template_selection,
            reply_markup=keyboards.generate_template_keyboard(
                config.INVITATION_TEMPLATE_PATH
            ),
        )
        message.author.set_state("TEMPLATE-SELECTION2-GROUP")

    @bot.on_message(conditions.at_state("TEMPLATE-SELECTION2-GROUP"))
    async def template_selection_state2(message: Message):
        if message.text == "بازگشت به مرحله قبل":
            await message.reply(
                texts.type_selection, reply_markup=keyboards.type_selection_group_menu
            )
            message.author.set_state("TYPE-SELECTION-GROUP")
            return

        template_name = message.text.split()[-1]

        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster.template = f"{poster.template}/{template_name}"
        Database.save_poster(poster)

        poster_type = get_poster_type(poster.template)
        await message.reply(
            texts.generate_heading2_message(poster_type), keyboards.return_menu
        )
        message.author.set_state("HEADING1-GROUP")

    @bot.on_message(conditions.at_state("HEADING1-GROUP"))
    async def heading1_state1(message: Message):
        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster_type = get_poster_type(poster.template)

        if message.text == "بازگشت به مرحله قبل":
            template_path = poster.template[
                : -1 * (len(poster.template.split("/")[-1]) + 1)
            ]
            template_grid = generate_template_grid(image_dir=template_path)
            await message.reply_photo(photo=template_grid)
            await message.reply(
                texts.template_selection,
                reply_markup=keyboards.generate_template_keyboard(template_path),
            )
            message.author.set_state("TEMPLATE-SELECTION2-GROUP")
            return

        if not validate_text(message.text, poster_type):
            await message.reply(texts.not_valid_length) 
            return
        
        poster.message_text = message.text
        Database.save_poster(poster)

        await message.reply(texts.generate_group_heading1_message(poster_type))
        message.author.set_state("FINAL-STATE-GROUP")

    @bot.on_message(conditions.at_state("FINAL-STATE-GROUP"))
    async def poster_generation_state(message: Message):
        poster = Database.load_posters_by_user(user_id=message.author.id)
        poster_type = get_poster_type(poster.template)

        if message.text == "بازگشت به مرحله قبل":
            await message.reply(
                texts.generate_heading2_message(poster_type), keyboards.return_menu
            )
            message.author.set_state("HEADING1-GROUP")
            return

        names = message.text.split("-")
        for name in names:
            poster.title = name
            poster.text_color = define_text_color(poster.template)
            final_bytes = process_poster_without_image(poster)

            uploaded_photo = await message.reply_photo(final_bytes)
            await message.reply_document(
                final_bytes, texts.completed_poster, reply_markup=keyboards.main_menu
            )

            poster.output_image = uploaded_photo.photo[-1].id

        Database.save_poster(poster)
        message.author.set_state("MAIN")
