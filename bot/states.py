from aiogram.fsm.state import State, StatesGroup


class AddActionStates(StatesGroup):

    action_name = State()
    action_date = State()
    action_description = State()