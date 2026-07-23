from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_segment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Офисы в аренду",
        callback_data="segment_offices"
    )
    builder.button(
        text="Торговые площади",
        callback_data="segment_retail"
    )
    builder.button(
        text="Гастропространство",
        callback_data="segment_gastro"
    )

    builder.adjust(1)
    return builder.as_markup()


def get_range_question_keyboard(options: list[str], show_back: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i, option in enumerate(options):
        builder.button(
            text=option,
            callback_data=f"ans_{i}"
        )

    if show_back:
        builder.button(text="⬅️ Назад", callback_data="go_back")

    builder.button(text="🔄 Начать сначала", callback_data="restart")

    builder.adjust(1)
    return builder.as_markup()

def get_callback_request_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Да, связаться со мной",
        callback_data="callback_yes"
    )
    builder.button(
        text="Нет, спасибо",
        callback_data="callback_no"
    )
    builder.button(
        text="⬅️ Назад",
        callback_data="go_back"
    )
    builder.button(
        text="🔄 Начать сначала",
        callback_data="restart"
    )

    builder.adjust(2)
    return builder.as_markup()

def get_just_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад",
        callback_data="go_back"
    )
    builder.button(
        text="🔄 Начать сначала",
        callback_data="restart"
    )

    builder.adjust(1)
    return builder.as_markup()