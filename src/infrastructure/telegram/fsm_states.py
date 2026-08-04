from aiogram.fsm.state import State, StatesGroup


class InputDataState(StatesGroup):
    waiting_data = State()


class OptionTwoState(StatesGroup):
    root = State()
