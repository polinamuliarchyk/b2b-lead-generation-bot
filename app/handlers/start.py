import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.google_sheets import log_action

from app.states.survey_states import SurveySG
from app.utils.texts import WELCOME_TEXT

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()

    await log_action(message.from_user.id, "start")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, интересно",
                    callback_data="start_survey"
                )
            ]
        ]
    )

    logo_path = os.path.join("app", "assets", "logobot.png")

    if os.path.exists(logo_path):
        photo = FSInputFile(logo_path)
        await message.answer_photo(
            photo=photo,
            caption=WELCOME_TEXT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=WELCOME_TEXT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


@router.callback_query(F.data == "start_survey")
async def process_start_survey(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(SurveySG.choose_segment)

    from app.keypads.user_kb import get_segment_keyboard
    from app.utils.texts import SEGMENT_CHOOSE_TEXT

    await callback.message.answer(
        text=SEGMENT_CHOOSE_TEXT,
        reply_markup=get_segment_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "/get_id")
async def get_chat_id(message: types.Message):
    print(f"ID ЭТОГО ЧАТА: {message.chat.id}")
    await message.answer(f"ID этого чата: {message.chat.id}")