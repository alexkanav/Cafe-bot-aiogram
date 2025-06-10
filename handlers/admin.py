from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states import Admin
from config import ADMIN_ID


router = Router()


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        buttons = [[KeyboardButton(text="food"), KeyboardButton(text="drink")]]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

        await message.answer("Choose category using the keyboard below.", reply_markup=keyboard)
        await state.set_state(Admin.waiting_for_choose_category)

    else:
        await message.answer("Access denied.")


@router.message(Admin.waiting_for_choose_category)
async def choose_category(message: Message, state: FSMContext):
    category = message.text.lower()
    await state.update_data(category=category)

    buttons = [[KeyboardButton(text="names"), KeyboardButton(text="size"), KeyboardButton(text="quantity")]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Choose item using the keyboard below.", reply_markup=keyboard)
    await state.set_state(Admin.waiting_for_choose_item)


@router.message(Admin.waiting_for_choose_item)
async def choose_item(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    item = message.text.lower()
    await state.update_data(item=item)

    await message.answer(f"Enter new items for {category}: {item}.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Admin.update_items)


@router.message(Admin.update_items)
async def update_menu(message: Message, state: FSMContext, db):
    user_data = await state.get_data()
    category = user_data.get("category")
    item = user_data.get("item")
    value = message.text.lower()
    array = value.split(', ')

    result = await db.update_menu(category, item, array)
    await message.answer(result)
    await state.clear()

