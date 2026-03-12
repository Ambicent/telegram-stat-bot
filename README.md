# 📊 Markets Forecast Telegram Bot

Telegram bot that automatically processes **Markets Forecast PDF reports** and calculates **daily room statistics**.

The bot reads tables from the PDF file and aggregates room counts by category for each day of the month.

---

## 🚀 Features

* 📄 Accepts **Markets Forecast PDF reports**
* 📊 Extracts room data from tables
* 🧮 Calculates totals for different booking categories
* 📅 Generates **daily statistics**
* 🤖 Works directly inside Telegram
* ⚡ Fast processing without saving files

---

## 📋 Example Output

```
Public Individual Direct Full: 12 10 11 14 15 ...

Public Individual Direct Disc: 5 4 6 7 3 ...

Public Individual Indirect Full: 3 2 1 4 ...

Public Individual Indirect Disc: 2 1 3 0 ...

Corporate Individual: 6 5 7 8 ...

Travel Agency Individual: 4 3 2 5 ...

Business Group: 1 2 3 4 ...

Leisure Group: 0 1 0 2 ...

Airlines: 0 0 1 0 ...
```

---

## 🛠 Requirements

Python **3.9+**

Install dependencies:

```
pip install -r requirements.txt
```

Dependencies:

* python-telegram-bot
* pdfplumber
* python-dotenv

---

## ⚙️ Setup

Create a `.env` file in the project folder:

```
BOT_TOKEN=your_telegram_bot_token
```

---

## ▶️ Run the bot

```
python stat_bot.py
```

You should see:

```
Bot started...
```

---

## 🤖 Usage

1. Open your bot in Telegram
2. Send the command:

```
/start
```

3. Upload a **Markets Forecast PDF report**

The bot will analyze the report and send back the calculated room statistics.

---

## 📁 Project Structure

```
.
├── stat_bot.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🔒 Security

The Telegram bot token is stored in a `.env` file and **not included in the repository**.

---

## 📜 License

MIT License
