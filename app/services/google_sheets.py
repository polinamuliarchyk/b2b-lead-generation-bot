import os
import datetime
import gspread_asyncio
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEETS_KEY, SERVICE_ACCOUNT_FILE

def get_creds():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    scoped = creds.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return scoped

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


async def save_lead_to_sheets(user_info: dict, survey_data: dict):
    try:
        agc = await agcm.authorize()
        sh = await agc.open_by_key(GOOGLE_SHEETS_KEY)
        worksheet = await sh.worksheet("Ответы и Лиды")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        answers = survey_data.get("answers", [])

        ans_1 = answers[0] if len(answers) > 0 else "—"
        ans_2 = answers[1] if len(answers) > 1 else "—"
        ans_3 = answers[2] if len(answers) > 2 else "—"
        ans_4 = answers[3] if len(answers) > 3 else "—"
        ans_5 = answers[4] if len(answers) > 4 else "—"
        ans_6 = answers[5] if len(answers) > 5 else "—"

        need_callback = "Да" if survey_data.get("need_callback") else "Нет"
        contact = survey_data.get("contact_info", "Не указан")

        row = [
            now,
            str(user_info.get("user_id")),
            survey_data.get("segment", "Не выбран"),
            ans_1,
            ans_2,
            ans_3,
            ans_4,
            ans_5,
            ans_6,
            contact,
            need_callback
        ]

        await worksheet.append_row(row)

    except Exception as e:
        print(f"❌ Ошибка при записи в Google Sheets: {e}")
        raise e


async def log_action(user_id: int, action: str):
    try:
        agc = await agcm.authorize()
        sh = await agc.open_by_key(GOOGLE_SHEETS_KEY)

        worksheet = await sh.worksheet("Логи")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            now,
            str(user_id),
            action
        ]

        await worksheet.append_row(row)

    except Exception as e:
        print(f"❌ Ошибка записи лога для действия '{action}': {e}")