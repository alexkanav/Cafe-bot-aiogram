import pytest
from unittest.mock import AsyncMock
from motor.motor_asyncio import AsyncIOMotorClient

from utils import MongoDB


@pytest.fixture
def mock_motor_client():
    """Mock the AsyncIOMotorClient and its collections."""
    # Mock the MongoDB collections
    mock_menu_collection = AsyncMock()
    mock_orders_collection = AsyncMock()

    # Mock the database
    mock_db = AsyncMock()
    mock_db["menu"] = mock_menu_collection
    mock_db["orders"] = mock_orders_collection

    # Mock the MongoDB client
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_client.__getitem__.return_value = mock_db

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [{"item": "Pizza", "category": "foods"}]

    # Mock find to return this mock cursor
    mock_menu_collection.find.return_value = mock_cursor

    # Mock update_one method for update_menu
    mock_update_result = AsyncMock()
    mock_update_result.modified_count = 1
    mock_update_result.matched_count = 1
    mock_menu_collection.update_one.return_value = mock_update_result

    return mock_client, mock_menu_collection, mock_cursor, mock_orders_collection


@pytest.mark.asyncio
async def test_mongodb_get_menu(mock_motor_client):
    """Test MongoDB's get_menu method."""
    mock_client, mock_menu_collection, mock_cursor, _ = mock_motor_client

    # Instantiate MongoDB with the mocked client
    db = MongoDB("mock_uri", menu_collection=mock_menu_collection)

    # Call get_menu() method
    await db.get_menu(mock_cursor)

    # Verify the menu was populated correctly
    assert db.menu == [{"item": "Pizza", "category": "foods"}]


@pytest.mark.asyncio
async def test_mongodb_update_menu(mock_motor_client):
    """Test MongoDB's update_menu method."""
    mock_client, mock_menu_collection, _, _ = mock_motor_client
    db = MongoDB("mock_uri", menu_collection=mock_menu_collection)
    db.client = mock_client

    # Call the update_menu method
    result = await db.update_menu("foods", "Pizza", ["Cheese", "Pepperoni"])

    # Verify the result
    assert result == "Matched 1, Modified 1"

    # Check the update_one method was called with the correct parameters
    mock_menu_collection.update_one.assert_called_once_with(
        {"category": "foods"},
        {"$set": {"Pizza": ["Cheese", "Pepperoni"]}}
    )


@pytest.mark.asyncio
async def test_mongodb_insert_order(mock_motor_client):
    """Test MongoDB's insert_order method."""
    mock_client, _, _, mock_orders_collection = mock_motor_client

    # Setup mock behavior
    mock_orders_collection.insert_one.return_value.inserted_id = "12345"

    db = MongoDB("mock_uri", orders_collection=mock_orders_collection)
    db.client = mock_client

    # Test inserting an order
    order_data = {"item": "Pizza", "quantity": 2}
    result = await db.insert_order(order_data)

    # Verify the result
    assert result == "12345"

    # Check insert_one was called with the correct data
    mock_orders_collection.insert_one.assert_called_once_with(order_data)
























# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from aiogram import Bot, Dispatcher
# from aiogram.fsm.storage.memory import MemoryStorage
# from main import main  # Assuming the code above is in 'your_module.py'
# from utils import MongoDB
# from middleware import DBMiddleware
# from handlers.common import router as common_router
# from handlers.foods import router as foods_router
# from handlers.drinks import router as drinks_router
# from handlers.admin import router as admin_router
# from configuration import BOT_TOKEN, URI
#
#
# @pytest.fixture
# def mock_bot():
#     """Mock the Bot to avoid hitting the Telegram API during tests."""
#     mock_bot = MagicMock(spec=Bot)
#     mock_bot.token = BOT_TOKEN
#     return mock_bot
#
#
# @pytest.fixture
# def mock_db():
#     """Mock the MongoDB instance."""
#     mock_db = MagicMock(spec=MongoDB)
#     mock_db.get_menu = AsyncMock()  # Mock the async method
#     return mock_db
#
#
# @pytest.fixture
# def mock_dispatcher(mock_db):
#     """Mock the Dispatcher and inject the mock DB middleware."""
#     dp = Dispatcher(storage=MemoryStorage())
#     dp.message.middleware(DBMiddleware(mock_db))  # Inject mock DB into dispatcher
#     dp.include_router(common_router)
#     dp.include_router(foods_router)
#     dp.include_router(drinks_router)
#     dp.include_router(admin_router)
#     return dp
#
#
# @pytest.mark.asyncio
# async def test_bot_initialization(mock_bot):
#     """Test if bot is initialized correctly."""
#     assert mock_bot.token == BOT_TOKEN
#     assert isinstance(mock_bot, Bot)
#
#
# @pytest.mark.asyncio
# async def test_mongo_db_connection(mock_db):
#     """Test the MongoDB connection and menu retrieval."""
#     await mock_db.get_menu()
#     mock_db.get_menu.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_dispatcher_includes_routers(mock_dispatcher):
#     """Test if all routers are included in the dispatcher."""
#     routers = [common_router, foods_router, drinks_router, admin_router]
#
#     for router in routers:
#         assert router in mock_dispatcher._routers
#
#
# @pytest.mark.asyncio
# async def test_commands_set(mock_bot):
#     """Test if the bot's commands are being set properly."""
#     from utils import set_commands
#     await set_commands(mock_bot)
#     mock_bot.set_my_commands.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_polling_start(mock_bot, mock_dispatcher):
#     """Test if the bot starts polling."""
#     # Simulate the bot polling process
#     mock_bot.delete_webhook = AsyncMock()
#     mock_dispatcher.start_polling = AsyncMock()
#
#     await mock_dispatcher.start_polling(mock_bot)
#
#     mock_dispatcher.start_polling.assert_called_once()
#     mock_bot.delete_webhook.assert_called_once_with(drop_pending_updates=True)
#
#
# @pytest.mark.asyncio
# async def test_main_function(mock_bot, mock_db, mock_dispatcher):
#     """Test the main function's flow."""
#     from unittest.mock import patch
#     with patch("main.set_commands") as mock_set_commands, \
#             patch("main.MongoDB", return_value=mock_db), \
#             patch("main.Bot", return_value=mock_bot), \
#             patch("main.Dispatcher", return_value=mock_dispatcher):
#         await main()
#         mock_set_commands.assert_called_once()
#         mock_db.get_menu.assert_called_once()
#         mock_dispatcher.include_router.assert_any_call(common_router)
#         mock_dispatcher.include_router.assert_any_call(foods_router)
#         mock_dispatcher.include_router.assert_any_call(drinks_router)
#         mock_dispatcher.include_router.assert_any_call(admin_router)
#
# # import pytest
# # from unittest.mock import AsyncMock, patch
# # from aiogram import Bot, Dispatcher, Router
# # from main import main
# # from middleware import DBMiddleware
# # from utils import MongoDB
# #
# #
# # @pytest.mark.asyncio
# # @patch("main.Bot", autospec=True)
# # @patch("main.Dispatcher", autospec=True)
# # @patch("main.set_commands", autospec=True)
# # @patch("main.MongoDB", autospec=True)
# # async def test_main(mock_mongo, mock_set_commands, mock_dispatcher, mock_bot):
# #     # Mock the bot and dispatcher
# #     mock_bot_instance = AsyncMock(spec=Bot)
# #     mock_dispatcher_instance = AsyncMock(spec=Dispatcher)
# #     mock_bot.return_value = mock_bot_instance
# #     mock_dispatcher.return_value = mock_dispatcher_instance
# #
# #     # Mock MongoDB initialization and get_menu
# #     mock_db_instance = AsyncMock(spec=MongoDB)
# #     mock_mongo.return_value = mock_db_instance
# #     mock_db_instance.get_menu = AsyncMock()
# #
# #     # Mock DBMiddleware
# #     mock_db_middleware = AsyncMock(spec=DBMiddleware)
# #
# #     # Patch the actual Router instances (assuming these are the real routers used)
# #     mock_common_router = AsyncMock(spec=Router)
# #     mock_foods_router = AsyncMock(spec=Router)
# #     mock_drinks_router = AsyncMock(spec=Router)
# #     mock_admin_router = AsyncMock(spec=Router)
# #
# #     # Mock the `message` attribute to avoid the AttributeError
# #     mock_dispatcher_instance.message = AsyncMock()
# #
# #     # Mocking dp.include_router behavior
# #     with patch.object(mock_dispatcher_instance, "include_router") as mock_include_router:
# #         # Call the main function
# #         await main()
# #
# #         # Assert the bot's delete_webhook is called
# #         mock_bot_instance.delete_webhook.assert_called_once_with(drop_pending_updates=True)
# #
# #         # Assert the dp.start_polling method is called
# #         mock_dispatcher_instance.start_polling.assert_called_once_with(mock_bot_instance)
# #
# #         # Assert that set_commands was called
# #         mock_set_commands.assert_called_once_with(mock_bot_instance)
# #
# #         # Assert MongoDB get_menu was called
# #         mock_db_instance.get_menu.assert_called_once()
# #
# #         # Ensure that the routers were included
# #         mock_include_router.assert_any_call(mock_common_router)
# #         mock_include_router.assert_any_call(mock_foods_router)
# #         mock_include_router.assert_any_call(mock_drinks_router)
# #         mock_include_router.assert_any_call(mock_admin_router)
# #
# #         # Ensure that the DBMiddleware is applied
# #         mock_dispatcher_instance.message.middleware.assert_called_once_with(mock_db_instance)




# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from motor.motor_asyncio import AsyncIOMotorClient
# from utils import MongoDB  # Replace with actual path to MongoDB class


from unittest.mock import patch

# @patch('utils.MongoDB')
# @pytest.mark.asyncio
# async def test_mongodb_get_menu(MockAsyncIOMotorClient):
#     # Create mock client and setup mock behavior
#     mock_client = AsyncMock(spec=AsyncIOMotorClient)
#     mock_db = AsyncMock()
#     mock_menu_collection = AsyncMock()
#     mock_cursor = AsyncMock()
#
#     # Define mock return values for the database and collections
#     mock_cursor.to_list.return_value = [{"item": "Pizza", "category": "foods"}]
#     mock_menu_collection.find.return_value = mock_cursor
#     mock_db["menu"] = mock_menu_collection
#     # mock_client["cafe"] = mock_db
#     mock_client = AsyncMock(spec=AsyncIOMotorClient)
#     mock_client.__getitem__.return_value = mock_db
#
#     # Ensure the MockAsyncIOMotorClient returns the mock client
#     MockAsyncIOMotorClient.return_value = mock_client
#
#     # Now instantiate MongoDB with the mocked client
#     db = MongoDB("mock_uri", client=mock_client, menu_collection=mock_menu_collection)
#
#     # Call get_menu() method
#     await db.get_menu(mock_cursor)
#
#     # Assert that the menu was populated correctly
#     assert db.menu == [{"item": "Pizza", "category": "foods"}]
#
#     # Verify that the find method was called once
#     # mock_menu_collection.find.assert_called_once()
#
#     # Verify that to_list was called
#     # mock_cursor.to_list.assert_called_once_with(length=None)




# @pytest.fixture
# def mock_motor_client():
#     """Mock the AsyncIOMotorClient and its collections."""
#     # Mock the MongoDB collections
#     mock_menu_collection = AsyncMock()
#     mock_orders_collection = AsyncMock()
#
#     # Mock the database
#     mock_db = AsyncMock()
#     mock_db["menu"] = mock_menu_collection
#     mock_db["orders"] = mock_orders_collection
#
#     # Mock the MongoDB client
#     mock_client = AsyncMock(spec=AsyncIOMotorClient)
#     mock_client.__getitem__.return_value = mock_db
#
#     return mock_client, mock_menu_collection, mock_orders_collection
#
#
# @pytest.mark.asyncio
# async def test_mongodb_get_menu(mock_motor_client):
#     """Test MongoDB's get_menu method."""
#     mock_client, mock_menu_collection, _ = mock_motor_client
#
#     # Setup mock behavior for to_list using AsyncMock
#     mock_cursor = AsyncMock()
#     mock_cursor.to_list.return_value = [{"item": "Pizza", "category": "foods"}]
#     mock_menu_collection.find.return_value = mock_cursor
#
#     # Instantiate MongoDB with the mocked client
#     db = MongoDB("mock_uri", menu_collection=mock_menu_collection, client=mock_client)
#
#     # Call get_menu() method
#     # await db.get_menu(mock_cursor)
#     with patch('your_module.AsyncIOMotorClient', autospec=True) as MockAsyncIOMotorClient:
#
#     # Verify the menu was populated correctly
#     assert db.menu == [{"item": "Pizza", "category": "foods"}]
#
#     # Check that the find method was called once
#     mock_menu_collection.find.assert_called_once()


# @pytest.mark.asyncio
# async def test_mongodb_update_menu(mock_motor_client):
#     """Test MongoDB's update_menu method."""
#     mock_client, mock_menu_collection, _ = mock_motor_client
#
#     # Setup mock behavior for update_one
#     mock_update_result = MagicMock()
#     mock_update_result.matched_count = 1
#     mock_update_result.modified_count = 1
#     mock_menu_collection.update_one.return_value = mock_update_result
#
#     # Instantiate MongoDB with the mocked client
#     db = MongoDB("mock_uri", client=mock_client)
#
#     # Call update_menu() method
#     result = await db.update_menu("foods", "Pizza", ["cheese", "tomato"])
#
#     # Verify the update result
#     assert result == "Matched 1, Modified 1"
#
#     # Check that update_one was called with the correct filter and update query
#     mock_menu_collection.update_one.assert_called_once_with(
#         {"category": "foods"},
#         {"$set": {"Pizza": ["cheese", "tomato"]}}
#     )
#
#
# @pytest.mark.asyncio
# async def test_mongodb_insert_order(mock_motor_client):
#     """Test MongoDB's insert_order method."""
#     mock_client, _, mock_orders_collection = mock_motor_client
#
#     # Setup mock behavior for insert_one
#     mock_insert_result = MagicMock()
#     mock_insert_result.inserted_id = "order_id_123"
#     mock_orders_collection.insert_one.return_value = mock_insert_result
#
#     # Instantiate MongoDB with the mocked client
#     db = MongoDB("mock_uri", client=mock_client)
#
#     # Call insert_order() method
#     order_data = {"item": "Pizza", "quantity": 2}
#     result = await db.insert_order(order_data)
#
#     # Verify that the result is the inserted order ID
#     assert result == "order_id_123"
#
#     # Check that insert_one was called with the correct order data
#     mock_orders_collection.insert_one.assert_called_once_with(order_data)
