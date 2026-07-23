# B2B Real Estate Lead Generation Bot

An asynchronous Telegram bot designed for commercial real estate agencies to automate client surveys, distribute marketing materials (PDF presentations), and collect leads directly into Google Sheets.

## Features

*   **Multi-step Interactive Surveys:** Utilizes `aiogram`'s Finite State Machine (FSM) to guide users through a structured questionnaire based on their property interests (Offices, Retail, Gastro).
*   **Automated Document Delivery:** Instantly sends targeted PDF presentations based on the user's selected business segment.
*   **Google Sheets Integration:** Automatically exports collected lead data and survey answers to a designated Google Spreadsheet in real-time.
*   **Instant Manager Notifications:** Forwards completed applications and contact requests to a private Telegram group for the sales team.
*   **Robust Deployment:** Configured to run 24/7 on a Linux VPS via a `systemd` service.

## Tech Stack

*   **Language:** Python 3
*   **Framework:** `aiogram` 3.x (Async Telegram Bot API)
*   **External APIs:** Google Sheets API, Google Drive API
*   **Infrastructure:** Linux (Ubuntu), systemd, SSH/SFTP

## Setup and Installation
1. Clone the repository:
Extract the project files into your chosen directory or clone the repo.

2. Create and activate a virtual environment:

``` bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate # For Windows
```

3. Install dependencies:

``` bash 
pip install -r requirements.txt
```

4. Environment Variables Setup:
Create a .env file in the root directory and add the following keys:

``` bash
BOT_TOKEN=your_telegram_bot_token
MANAGERS_CHAT_ID=-1001234567890
GOOGLE_SHEET_URL=your_google_sheet_link
```
5. Google API Credentials:
Place your google_credentials.json file in the root directory to enable Google Sheets integration.

6. Run the bot:

``` bash 
python main.py
```

## Project Structure
* main.py — Entry point and bot initialization.

* app/handlers/ — Contains routers and survey logic (FSM).

* app/assets/pdfs/ — Directory for segment-specific PDF presentations.

* config.py — Environment variables and configuration management.

* requirements.txt — Project dependencies.