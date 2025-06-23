import pytest
from unittest.mock import AsyncMock

from utils import set_commands


@pytest.mark.asyncio
async def test_set_commands():
    """Test if set_commands correctly sets the commands for the bot."""

    # Create a mock bot with an async set_my_commands method
    mock_bot = AsyncMock()
    mock_bot.set_my_commands = AsyncMock()

    await set_commands(mock_bot)

    # Check that set_my_commands was called exactly once
    assert mock_bot.set_my_commands.call_count == 1

    # Verify the exact list of commands passed
    commands_arg = mock_bot.set_my_commands.call_args[0][0]
    assert any(cmd.command == "table" for cmd in commands_arg)

