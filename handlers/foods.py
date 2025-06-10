from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states import OrderFoods


router = Router()


@router.message(Command("foods"))
@router.message(OrderFoods.waiting_for_foods_menu)
async def foods_start(message: Message, state: FSMContext, db):
    data = await state.get_data()
    items = data.get("chosen_table")
    if not items:
        return

    buttons = [[KeyboardButton(text=name)] for name in db.menu[1]['names']]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Select a food:", reply_markup=keyboard)
    await state.set_state(OrderFoods.waiting_for_foods_name)


@router.message(OrderFoods.waiting_for_foods_name)
async def foods_chosen(message: Message, state: FSMContext, db):
    food = message.text.lower()
    if food not in db.menu[1]['names']:
        await message.answer("Please select a food using the keyboard below.")
        await foods_start(message, state)
        return

    await state.update_data(chosen_food=food)
    await foods_size_chosen(message, state, db)


async def foods_size_chosen(message: Message, state: FSMContext, db):
    buttons = [[KeyboardButton(text=name)] for name in db.menu[1]['size']]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Now select your serving size:", reply_markup=keyboard)
    await state.set_state(OrderFoods.waiting_for_foods_size)


@router.message(OrderFoods.waiting_for_foods_size)
async def foods_size_set(message: Message, state: FSMContext, db):
    size = message.text.lower()
    if size not in db.menu[1]['size']:
        await message.answer("Please select the serving size using the keyboard below.")
        await foods_size_chosen(message, state, db)
        return

    await state.update_data(chosen_food_size=size)
    await message.answer("Enter the quantity (1–10):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderFoods.waiting_for_foods_quantity)


@router.message(OrderFoods.waiting_for_foods_quantity)
async def drink_quantity_set(message: Message, state: FSMContext, db):
    quantity = message.text.lower()
    if quantity not in db.menu[1]['allowed_quantities']:
        await message.answer("Enter a valid quantity (1–10).")
        return

    user_data = await state.get_data()
    new_order = [user_data['chosen_food'], user_data['chosen_food_size'], quantity]

    items = user_data.get("orders", [])
    items.append(new_order)
    await state.update_data(orders=items)
    await state.set_state(None)
    food_key = f"{user_data['chosen_food']}-{user_data['chosen_food_size']}"
    buttons = [[KeyboardButton(text=i)] for i in ("/foods", "/drinks", "/apply", "/cancel")]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer(
        f"You ordered {quantity}x {food_key}.\n\n"
        "Order more:\n  /foods\n  /drinks\n  /apply\n  /cancel",
        reply_markup=keyboard
    )
    await state.set_state(None)

