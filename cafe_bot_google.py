import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text, IDFilter
import requests
from config import *


def receive_menu_from_google():
    global available_dishes_names, available_dishes_sizes, available_drinks_names, available_drinks_sizes
    CREDENTIALS_FILE = 'my.json'  # private key file name
    spredsheets_id = sheets_id  # Google sheet id
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    # read from google sheet
    values = service.spreadsheets().values().get(
        spreadsheetId=spredsheets_id,
        range='B3:Z6',
        majorDimension='ROWS'
    ).execute()

    available_dishes_names = values.get('values')[0]
    available_dishes_sizes = values.get('values')[1]
    available_drinks_names = values.get('values')[2]
    available_drinks_sizes = values.get('values')[3]


async def send_telegram(text: str):
    token = tok  # telegram token
    url = "https://api.telegram.org/bot"
    channel_id = ch_id  # telegram channel id
    url += token
    method = url + "/sendMessage"
    r = requests.post(method, data={"chat_id": channel_id, "text": text})

    if r.status_code != 200:
        raise Exception("post_text error")


class OrderTable(StatesGroup):
    waiting_for_table_number = State()
    waiting_for_dishes_or_drink = State()
    waiting_for_order = State()


class OrderDishes(StatesGroup):
    waiting_for_dishes_name = State()
    waiting_for_dishes_size = State()
    waiting_for_dishes_menu = State()
    waiting_for_dishes_quantity = State()


class OrderDrinks(StatesGroup):
    waiting_for_drink_name = State()
    waiting_for_drink_size = State()
    waiting_for_drink_menu = State()
    waiting_for_drink_quantity = State()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/table", description="Your table number"),
        BotCommand(command="/drinks", description="Order drinks"),
        BotCommand(command="/dishes", description="Order dishes"),
        BotCommand(command="/cancel", description="Cancel")
    ]
    await bot.set_my_commands(commands)


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_start, commands="table", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="cancel", ignore_case=True), state="*")
    dp.register_message_handler(admin_command, IDFilter(user_id=admin_id), commands="admin")
    dp.register_message_handler(table_chosen, state=OrderTable.waiting_for_table_number)
    dp.register_message_handler(select_f_d, state=OrderTable.waiting_for_dishes_or_drink)
    dp.register_message_handler(order, commands="order", state="*")
    dp.register_message_handler(order2, state=OrderTable.waiting_for_order)


def register_handlers_dishes(dp: Dispatcher):
    dp.register_message_handler(dishes_start, commands="dishes", state="*")
    dp.register_message_handler(dishes_start, state=OrderDishes.waiting_for_dishes_menu)
    dp.register_message_handler(dishes_chosen, state=OrderDishes.waiting_for_dishes_name)
    dp.register_message_handler(dishes_size_set, state=OrderDishes.waiting_for_dishes_size)
    dp.register_message_handler(dishes_quantity, state=OrderDishes.waiting_for_dishes_quantity)


def register_handlers_drinks(dp: Dispatcher):
    dp.register_message_handler(drinks_start, commands="drinks", state="*")
    dp.register_message_handler(drinks_start, state=OrderDrinks.waiting_for_drink_menu)
    dp.register_message_handler(drinks_chosen, state=OrderDrinks.waiting_for_drink_name)
    dp.register_message_handler(drinks_size_set, state=OrderDrinks.waiting_for_drink_size)
    dp.register_message_handler(drink_quantity, state=OrderDrinks.waiting_for_drink_quantity)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for number in available_table:
        keyboard.insert(number)
    await message.answer("Enter your table number", reply_markup=keyboard)
    await OrderTable.waiting_for_table_number.set()


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    if message['from']['id'] in orders:
        del orders[message['from']['id']]
    await message.answer("Action canceled")
    await cmd_start(message, state)


async def admin_command(message: types.Message):
    await message.answer("admin commands")


async def table_chosen(message: types.Message, state: FSMContext):
    table = message.text.lower()
    if message.text.lower() not in available_table:
        await message.answer("Select a table using the keyboard below.")
        await cmd_start(message, state)
        return

    orders[message['from']['id']] = {'table': table}
    orders[message['from']['id']]['dishes'] = {}
    orders[message['from']['id']]['drinks'] = {}
    await state.update_data(chosen_table=message.text.lower())
    await chosen_f_d(message)


async def chosen_f_d(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('dishes', 'drinks')
    await message.answer("Select what you want to order: \n     /drinks   \n     /dishes  .",
                         reply_markup=keyboard)
    await OrderTable.waiting_for_dishes_or_drink.set()


async def select_f_d(message: types.Message, state):
    res = message.text.lower()
    if res == '/drinks':
        await drinks_start(message)
    elif res == '/dishes':
        await dishes_start(message)
    elif res == '/order':
        await order(message)
    elif res == '/cancel':
        await cmd_cancel(message, state)
    else:
        await message.answer("Select what you want to order using the keyboard.")
        await chosen_f_d(message)

        return


async def order(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('send', 'cancel')
    await message.answer(f"You ordered:{orders[message['from']['id']]['dishes']} , {orders[message['from']['id']]['drinks']}")
    await message.answer("Check and submit your order:\n   /send\n   /cancel", reply_markup=keyboard)
    await OrderTable.waiting_for_order.set()


async def order2(message: types.Message, state):
    if message.text.lower() == 'cancel' or message.text.lower() == '/cancel':
        await cmd_cancel(message, state)
    elif message.text.lower() == 'send' or message.text.lower() == '/send':
        await message.answer("Thank you, your order has been accepted, please wait")
        await send_telegram(f"Order {orders}")
        del orders[message['from']['id']]
        await state.finish()
    else:
        await message.answer("Make your choice using the keyboard")

        return


async def dishes_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_dishes_names:
        keyboard.add(name)
    await message.answer("Select dish:", reply_markup=keyboard)
    await OrderDishes.waiting_for_dishes_name.set()


async def dishes_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_dishes_names:
        await message.answer("Please select a dish using the keyboard below.")
        await dishes_start(message)
        return

    await state.update_data(chosen_dishes=message.text.lower())
    await dishes_size_chosen(message, state)


async def dishes_size_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_dishes_sizes:
        keyboard.add(size)
    await message.answer("Now select your serving size:", reply_markup=keyboard)
    await OrderDishes.waiting_for_dishes_size.set()


async def dishes_size_set(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_dishes_sizes:
        await message.answer("Please select your serving size using the keyboard below.")
        await dishes_size_chosen(message, state)
        return

    await state.update_data(chosen_dishes_size=message.text.lower())
    await message.answer("Please select the required quantity.", reply_markup=types.ReplyKeyboardRemove())
    await OrderDishes.waiting_for_dishes_quantity.set()


async def dishes_quantity(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_quantity:
        await message.answer("Enter the correct quantity using numbers from 1 to 10.")
        return

    await state.update_data(dishes_quantity=message.text.lower())
    user_data = await state.get_data()
    orders[message['from']['id']]['dishes'].update({f"{user_data['chosen_dishes']}-{user_data['chosen_dishes_size']}": f"{user_data['dishes_quantity']}"})
    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('dishes', 'drinks', 'apply')
    keyboard.add('cancel')
    await message.answer(f"You ordered {message.text.lower()} servings {user_data['chosen_dishes']}-{user_data['chosen_dishes_size']}.\n"
                         f"Order more \n  /dishes \n   /drinks \n   /order\n   /cancel", reply_markup=keyboard)
    await OrderTable.waiting_for_dishes_or_drink.set()


async def drinks_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_drinks_names:
        keyboard.add(name)
    await message.answer("Choose a drink:", reply_markup=keyboard)
    await OrderDrinks.waiting_for_drink_name.set()


async def drinks_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_names:
        await message.answer("Please select a drink using the keyboard below.")
        await drinks_start(message)
        return

    await state.update_data(chosen_drink=message.text.lower())
    await drinks_size_chosen(message, state)


async def drinks_size_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_drinks_sizes:
        keyboard.add(size)
    await message.answer("Now select the drink volume:", reply_markup=keyboard)
    await OrderDrinks.waiting_for_drink_size.set()


async def drinks_size_set(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_sizes:
        await message.answer("Please select serving size, using the keyboard below.")
        await drinks_size_chosen(message, state)
        return

    await state.update_data(chosen_drink_size=message.text.lower())
    await message.answer("Please select the required quantity.", reply_markup=types.ReplyKeyboardRemove())
    await OrderDrinks.waiting_for_drink_quantity.set()


async def drink_quantity(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_quantity:
        await message.answer("Enter the correct quantity using numbers from 1 to 10.")
        return

    await state.update_data(drink_quantity=message.text.lower())
    user_data = await state.get_data()
    orders[message['from']['id']]['drinks'].update({f"{user_data['chosen_drink']}-{user_data['chosen_drink_size']}": f"{user_data['drink_quantity']}"})
    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('dishes', 'drinks', 'apply')
    keyboard.add('cancel')
    await message.answer(f"You ordered {message.text.lower()} servings {user_data['chosen_drink']}-{user_data['chosen_drink_size']}.\n"
                         f"Order more \n   /dishes\n    /drinks, \n    /order\n   /cancel",
                         reply_markup=keyboard)
    await OrderTable.waiting_for_dishes_or_drink.set()


async def main():
    # logging to stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    bot = Bot(token=bot_token)  # telegram token
    dp = Dispatcher(bot, storage=MemoryStorage())
    adm_id = admin_id  # administrator id in telegram

    register_handlers_common(dp, adm_id)
    register_handlers_drinks(dp)
    register_handlers_dishes(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


receive_menu_from_google()
logger = logging.getLogger(__name__)

asyncio.run(main())
