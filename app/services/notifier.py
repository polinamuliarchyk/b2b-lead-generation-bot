from aiogram import Bot
from config import MANAGERS_CHAT_ID  # ID чата менеджеров из .env


async def send_manager_notification(bot: Bot, survey_data: dict):
    if not MANAGERS_CHAT_ID:
        print("⚠️ MANAGERS_CHAT_ID не задан в .env, пропуск отправки уведомления.")
        return

    segment = survey_data.get("segment", "Не выбран")
    need_callback = "<b>Да</b>" if survey_data.get("need_callback") else "Нет"
    contact = survey_data.get("contact_info", "Не указан")

    text = (
        f"<b>Новый ответ!</b>\n\n"
        f"<b>Сегмент:</b> {segment}\n\n"
        f"<b>Запрошен звонок:</b> {need_callback}\n"
        f"<b>Контакт:</b> {contact}"
    )

    try:
        await bot.send_message(
            chat_id=MANAGERS_CHAT_ID,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления менеджерам: {e}")
        raise e