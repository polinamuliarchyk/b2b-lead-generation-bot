import asyncio
import os

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile

from app.keypads.user_kb import get_segment_keyboard, get_range_question_keyboard, get_callback_request_keyboard, \
    get_just_back_keyboard
from app.services.google_sheets import save_lead_to_sheets
from app.services.google_sheets import log_action
from app.services.notifier import send_manager_notification
from app.states.survey_states import SurveySG
from app.utils.texts import QUESTIONS_BY_SEGMENT, NO_CALLBACK_FINAL_TEXT, SEGMENT_CHOOSE_TEXT

router = Router()

@router.callback_query(SurveySG.choose_segment, F.data.startswith("segment_"))
async def process_segment_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await log_action(callback.from_user.id, "segment")

    segment_map = {
        "segment_offices": "Офисы в аренду",
        "segment_retail": "Торговые площади",
        "segment_gastro": "Гастропространство"
    }

    pdf_map = {
        "segment_offices": "office.pdf",
        "segment_retail": "retail.pdf",
        "segment_gastro": "gastro.pdf"
    }

    selected_segment = segment_map.get(callback.data, "Офисы в аренду")
    pdf_filename = pdf_map.get(callback.data)

    await state.update_data(segment=selected_segment, answers=[])

    try:
        await callback.message.delete()
    except Exception:
        pass

    if pdf_filename:
        pdf_path = os.path.join("app", "assets", pdf_filename)

        if os.path.exists(pdf_path):
            document = FSInputFile(pdf_path)

            await callback.message.answer_document(
                document=document,
                caption=f"Прекрасный выбор! Вот наша презентация по  «{selected_segment}». Вы можете изучить ее в любое время. "
                        f"А теперь, если позволите, несколько уточнений, чтобы наше будущее предложение было максимально точным."
            )
        else:
            print(f"Ошибка: Файл презентации не найден по пути {pdf_path}")

    await state.set_state(SurveySG.answering_questions)

    await show_question(callback.message, state, question_index=0)


async def show_question(message: types.Message, state: FSMContext, question_index: int):
    user_data = await state.get_data()
    segment = user_data.get("segment")
    questions = QUESTIONS_BY_SEGMENT.get(segment, [])

    if question_index < len(questions):
        current_q = questions[question_index]
        kb = get_range_question_keyboard(options=current_q["options"], show_back=True) if current_q.get(
            "type") == "choice" else get_just_back_keyboard()

        try:
            await message.edit_text(
                text=f"<b>Вопрос {question_index + 1}/{len(questions)}:</b>\n\n{current_q['text']}",
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception:
            await message.answer(
                text=f"<b>Вопрос {question_index + 1}/{len(questions)}:</b>\n\n{current_q['text']}",
                reply_markup=kb,
                parse_mode="HTML"
            )
    else:
        await log_action(message.chat.id, "finish")
        await state.set_state(SurveySG.asking_for_callback)

        await message.answer(
            text="Благодарим за Ваше участие! Мы ценим ваше время и мнение.\nС Уважением, Команда МФК «Газпром Центр».",
            parse_mode="HTML"
        )
        await message.answer(
            text="Хотите, наш менеджер свяжется с вами в приоритетном порядке и предоставит персональное предложение, как только оно будет сформировано?",
            reply_markup=get_callback_request_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(SurveySG.answering_questions, F.data.startswith("ans_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    user_data = await state.get_data()
    answers = user_data.get("answers", [])
    segment = user_data.get("segment")

    questions = QUESTIONS_BY_SEGMENT.get(segment, [])
    current_q_index = len(answers)

    if current_q_index < len(questions):
        current_q = questions[current_q_index]
        option_index = int(callback.data.replace("ans_", ""))
        selected_answer_text = current_q["options"][option_index]

        if "свой вариант" in selected_answer_text.lower():
            await state.set_state(SurveySG.waiting_for_custom_answer)

            kb = get_just_back_keyboard()
            await callback.message.edit_text(
                text="Интересно! Расскажите подробнее — какой вариант вы предлагаете?\n\n<i>(Напишите ответ текстом в чат)</i>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            return

        answers.append(selected_answer_text)
        await state.update_data(answers=answers)

    await show_question(callback.message, state, question_index=len(answers))


@router.message(SurveySG.waiting_for_custom_answer, F.text)
async def process_custom_text_answer(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    answers = user_data.get("answers", [])

    answers.append(f"Свой вариант: {message.text}")
    await state.update_data(answers=answers)
    await state.set_state(SurveySG.answering_questions)
    await show_question(message, state, question_index=len(answers))


@router.callback_query(SurveySG.asking_for_callback, F.data == "callback_no")
async def process_callback_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(need_callback=False, contact_info="Не указан (отказ)")

    user_data = await state.get_data()
    user_info = {
        "user_id": callback.from_user.id,
        "username": callback.from_user.username or "Нет юзернейма",
        "full_name": callback.from_user.full_name
    }

    try:
        await save_lead_to_sheets(user_info=user_info, survey_data=user_data)
        await send_manager_notification(bot=callback.bot, survey_data=user_data)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

    await callback.message.edit_text(
        text=NO_CALLBACK_FINAL_TEXT,
        parse_mode="HTML"
    )

    await state.clear()


@router.callback_query(SurveySG.asking_for_callback, F.data == "callback_yes")
async def process_callback_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(need_callback=True)
    await state.set_state(SurveySG.waiting_for_contact)

    text = (
        "Отлично! Пожалуйста, оставьте ваш контактный телефон или email для связи. "
        "Нажимая «Отправить», вы соглашаетесь с "
        "<a href='https://docs.google.com/document/d/1zCYzSA0pwgo-aQ2m1bHmNtD7SBmHfz5QIAjRWsCsmC8/edit?usp=sharing'>"
        "политикой обработки персональных данных</a>."
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(SurveySG.waiting_for_contact)
async def process_contact_info(message: types.Message, state: FSMContext):
    await state.update_data(contact_info=message.text)

    user_data = await state.get_data()
    user_info = {
        "user_id": message.from_user.id,
        "username": message.from_user.username or "Нет юзернейма",
        "full_name": message.from_user.full_name
    }

    try:
        from app.services.google_sheets import save_lead_to_sheets
        from app.services.notifier import send_manager_notification
        await log_action(message.from_user.id, "contact")
        await save_lead_to_sheets(user_info=user_info, survey_data=user_data)
        await send_manager_notification(bot=message.bot, survey_data=user_data)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

    await message.answer(
        text="Спасибо! Мы внесли вас в приоритетный список. Наш менеджер свяжется с вами в ближайшее время.",
        parse_mode="HTML"
    )

    await state.clear()


@router.callback_query(StateFilter(SurveySG.answering_questions, SurveySG.waiting_for_custom_answer),
                       F.data == "go_back")
async def process_go_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    current_state = await state.get_state()
    user_data = await state.get_data()
    answers = user_data.get("answers", [])

    if current_state == SurveySG.waiting_for_custom_answer:
        await state.set_state(SurveySG.answering_questions)
        await show_question(callback.message, state, question_index=len(answers))

    else:
        if answers:
            answers.pop()
            await state.update_data(answers=answers)
            await show_question(callback.message, state, question_index=len(answers))
        else:
            await state.set_state(SurveySG.choose_segment)
            await callback.message.edit_text(
                text="Какой тип площадей вас интересует в первую очередь?",
                reply_markup=get_segment_keyboard()
            )


@router.callback_query(F.data == "restart")
async def process_restart(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(SurveySG.choose_segment)

    try:
        await callback.message.edit_text(
            text=SEGMENT_CHOOSE_TEXT,
            reply_markup=get_segment_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text=SEGMENT_CHOOSE_TEXT,
            reply_markup=get_segment_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(SurveySG.asking_for_callback, F.data.in_(["go_back", "go_back_from_final"]))
async def process_go_back_from_final(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    user_data = await state.get_data()
    answers = user_data.get("answers", [])

    if answers:
        answers.pop()
        await state.update_data(answers=answers)

    await state.set_state(SurveySG.answering_questions)
    await show_question(callback.message, state, question_index=len(answers))

