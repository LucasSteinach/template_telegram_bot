
from aiogram.fsm.state import StatesGroup, State


class MainMenuState(StatesGroup):
    root: State()


class OptionOneState(StatesGroup):
    root: State()


class OptionTwoState(StatesGroup):
    root: State()
