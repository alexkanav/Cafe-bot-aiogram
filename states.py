from aiogram.fsm.state import State, StatesGroup


class OrderTable(StatesGroup):
    waiting_for_table_number: State = State()
    waiting_for_foods_or_drink: State = State()
    waiting_for_order: State = State()


class OrderFoods(StatesGroup):
    waiting_for_foods_name: State = State()
    waiting_for_foods_size: State = State()
    waiting_for_foods_menu: State = State()
    waiting_for_foods_quantity: State = State()


class OrderDrinks(StatesGroup):
    waiting_for_drink_name: State = State()
    waiting_for_drink_size: State = State()
    waiting_for_drink_menu: State = State()
    waiting_for_drink_quantity: State = State()


class Admin(StatesGroup):
    waiting_for_choose_category: State = State()
    waiting_for_choose_item: State = State()
    update_items: State = State()

