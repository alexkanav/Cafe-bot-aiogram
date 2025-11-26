# Telegram Cafe Ordering Bot

A fully functional Telegram bot for ordering food and drinks in a cafe, built with **Aiogram v3**. The bot uses **MongoDB** to store menu items and orders, and leverages asynchronous operations for fast, scalable data handling — making it suitable for real-world cafe workflows.

---

## Features

### Display full cafe menu
- Includes food and drinks, organized into categories.

### Take and process customer orders 
- Users can browse the menu, add items, and confirm their order directly in Telegram.

### Asynchronous menu updates
- Admins can add, remove, or modify menu items without blocking the bot.

### Telegram bot commands
- Easy interaction through commands like /menu, /order, and admin tools.

### Async MongoDB integration
- Fast and scalable database operations using an asynchronous Mongo client.

### Order persistence
- Orders saved in JSON format for logging, analytics, or receipts.

### Admin command handling

### Simple deployment
- Easily deploy on Heroku, Railway, Render, or any VPS.

---

## Tech Stack

- [Python 3.11+](https://www.python.org)
- [Aiogram v3](https://docs.aiogram.dev/)
- MongoDB (local or cloud: MongoDB Atlas)
- Telegram Bot API

---

## Setup

### 1. Clone and Install

    git clone https://github.com/alexkanav/Cafe-bot-aiogram
    cd cafe-bot-aiogram

### 2. Create a Virtual Environment    
    python -m venv venv
    source venv/bin/activate      # or venv\Scripts\activate on Windows
    
    
### 3. Install Dependencies
    pip install -r requirements.txt

### 4. Configure the Bot Token and MongoDB URI

### 5. Run the Bot
    python main.py

---

## License

MIT License. Free for personal and commercial use. Credit appreciated!


