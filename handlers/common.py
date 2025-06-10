from aiogram import Router, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils import send_to_telegram
from states import OrderTable
from config import AVAILABLE_TABLES


router = Router()


@router.message(CommandStart())
@router.message(Command("table"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardBuilder()
    for i in AVAILABLE_TABLES:
        builder.add(types.KeyboardButton(text=i))
    builder.adjust(4)
    await message.answer("Select a table.", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderTable.waiting_for_table_number)


@router.message(Command("cancel"))
@router.message(F.text.lower() == "cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Action canceled.", reply_markup=ReplyKeyboardRemove())
    await cmd_start(message, state)


@router.message(OrderTable.waiting_for_table_number)
async def table_chosen(message: Message, state: FSMContext):
    table = message.text.strip().lower()
    if table not in AVAILABLE_TABLES:
        await message.answer("Select a table using the keyboard below.")
        await cmd_start(message, state)
        return

    await state.update_data(chosen_table=table)
    await chosen_foods_drinks(message, state)


async def chosen_foods_drinks(message: Message, state: FSMContext):
    await state.set_state(None)
    buttons = [[KeyboardButton(text="/foods"), KeyboardButton(text="/drinks")]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(
        "What would you like to order?\n   /drinks\n   /foods",
        reply_markup=keyboard
    )


@router.message(Command("apply"))
async def order(message: Message, state: FSMContext, db):
    user_data = await state.get_data()
    items = user_data.get("orders", [])
    if not items:
        await message.answer("You haven't ordered anything.")
    else:
        order_data = {
            "user_id": message.from_user.id,
            "items": items
        }
        order_id = await db.insert_order(order_data)
        remove_keyboard = types.ReplyKeyboardRemove()
        await message.answer("Thanks.", reply_markup=remove_keyboard)
        await message.answer(f"✅ Order placed! ID: {order_id}")
        await send_to_telegram(f"ID: {order_id} Order: {order_data}")
    await state.clear()

