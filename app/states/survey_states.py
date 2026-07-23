from aiogram.fsm.state import State, StatesGroup


class SurveySG(StatesGroup):
    choose_segment = State()
    answering_questions = State()
    waiting_for_custom_answer = State()
    asking_for_callback = State()
    waiting_for_contact = State()

class AdminSG(StatesGroup):
    main_menu = State()