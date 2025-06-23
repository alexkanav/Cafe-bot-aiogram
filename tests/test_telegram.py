import pytest
from unittest.mock import AsyncMock, patch

from utils import send_to_telegram


pytestmark = pytest.mark.asyncio


@patch("aiohttp.ClientSession.post")
async def test_send_to_telegram_success(mock_post):
    """Test if send_to_telegram sends a message to the Telegram channel."""

    # Mock the response to simulate a 200 OK
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_post.return_value.__aenter__.return_value = mock_response

    text = "Hello"
    await send_to_telegram(text, "fake_token",  "fake_channel")

    # Verify the POST request was made
    mock_post.assert_called_once()
    url = f"https://api.telegram.org/botfake_token/sendMessage"
    mock_post.assert_called_with(url, data={"chat_id": "fake_channel", "text": text})


@patch("aiohttp.ClientSession.post")
async def test_send_to_telegram_failure(mock_post):
    """Test if send_to_telegram raises an exception when the response status is not 200."""
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_post.return_value.__aenter__.return_value = mock_response

    with pytest.raises(Exception, match="post text error"):
        await send_to_telegram("Test failure", "fake_token",  "fake_channel")






