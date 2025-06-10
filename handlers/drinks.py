from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states import OrderDrinks


router = Router()


@router.message(Command("drinks"))
@router.message(OrderDrinks.waiting_for_drink_menu)
async def drinks_start(message: Message, state: FSMContext, db):
    data = await state.get_data()
    items = data.get("chosen_table")
    if not items:
        return

    buttons = [[KeyboardButton(text=name)] for name in db.menu[0]['names']]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Choose a drink:", reply_markup=keyboard)
    await state.set_state(OrderDrinks.waiting_for_drink_name)


@router.message(OrderDrinks.waiting_for_drink_name)
async def drinks_chosen(message: Message, state: FSMContext, db):
    drink = message.text.lower()
    if drink not in db.menu[0]['names']:
        await message.answer("Please select a drink using the keyboard below.")
        await drinks_start(message, state)
        return

    await state.update_data(chosen_drink=drink)
    await drinks_size_chosen(message, state, db)


async def drinks_size_chosen(message: Message, state: FSMContext, db):
    buttons = [[KeyboardButton(text=name)] for name in db.menu[0]['size']]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Now select the drink volume:", reply_markup=keyboard)
    await state.set_state(OrderDrinks.waiting_for_drink_size)


@router.message(OrderDrinks.waiting_for_drink_size)
async def drinks_size_set(message: Message, state: FSMContext, db):
    size = message.text.lower()
    if size not in db.menu[0]['size']:
        await message.answer("Please select serving size using the keyboard below.")
        await drinks_size_chosen(message, state, db)
        return

    await state.update_data(chosen_drink_size=size)
    await message.answer("Enter the quantity (1–10):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderDrinks.waiting_for_drink_quantity)


@router.message(OrderDrinks.waiting_for_drink_quantity)
async def drink_quantity_set(message: Message, state: FSMContext, db):
    quantity = message.text.lower()
    if quantity not in db.menu[0]['allowed_quantities']:
        await message.answer("Enter a valid quantity (1–10).")
        return

    user_data = await state.get_data()
    new_order = [user_data['chosen_drink'], user_data['chosen_drink_size'], quantity]

    items = user_data.get("orders", [])
    items.append(new_order)
    await state.update_data(orders=items)
    await state.set_state(None)
    drink_key = f"{user_data['chosen_drink']}-{user_data['chosen_drink_size']}"
    buttons = [[KeyboardButton(text=i)] for i in ("/foods", "/drinks", "/apply", "/cancel")]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer(
        f"You ordered {quantity}x {drink_key}.\n\n"
        "Order more:\n  /foods\n  /drinks\n  /apply\n  /cancel",
        reply_markup=keyboard
    )
    await state.set_state(None)
