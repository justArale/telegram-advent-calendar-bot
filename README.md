# 🎄 Telegram Advent Riddle Bot

Built for a personal Advent project, this bot combines my love for coding, riddles, and the festive countdown to Christmas — all wrapped up in one fun, Python-powered experience with Christmas spirit 🎄

Each day in December unlocks a new riddle — In my setup: some written in text, others in code.  
Solving a riddle reveals a unique emoji — That emoji marks the matching present waiting to be unwrapped! 🎁

This Telegram bot turns a classic self-made Advent calendar into a daily riddle challenge — because writing plain numbers on gifts felt just too boring.

*(But you can easily adapt the database and logic to fit your own Advent twist!)*

---

## 📚 Table of Contents

- [🎄 Telegram Advent Riddle Bot](#telegram-advent-riddle-bot)
- [✨ Features](#features)
- [🧠 Tech Stack](#tech-stack)
- [📁 Project Structure](#project-structure)
- [⚙️ Prerequisites](#prerequisites)
- [💻 Installation](#installation)
  - [Local Development](#local-development)
  - [Production Deployment (Docker)](#production-deployment-docker)
- [🗄️ Database Schema](#️database-schema)
- [🤖 Bot Commands](#bot-commands)
- [📄 License](#license)

---

## ✨ Features

- 🎁 **24 Daily Riddles** - Solve today's riddle with `/riddle`
- 🍬 **Past Riddle Access** - Solve previous days' riddles with `/riddle{day}`
- 🚫 **No Spoilers** - Can't access future riddles before they unlock
- 🐳 **Docker Support** - Easy deployment with Docker Compose
- 🌍 **Timezone Aware** - Configurable timezone support
- 🔄 **Dual Environment** - Separate development and production setups
- 📊 **JSONB Answers** - Multiple valid answer formats per riddle

---

## 🧠 Tech Stack

- **Language**: Python 3.11
- **Framework**: python-telegram-bot 20.7
- **Database**: NeonDB (PostgreSQL)
- **Deployment**: Docker / Docker Compose
- **Environment Management**: python-dotenv

---

## 📁 Project Structure
```
telegram-advent-calendar-bot/
├── bot.py                      # Production bot
├── bot_dev.py                  # Development bot
├── bot_core.py                 # Shared bot logic
├── setup_db.py                 # Database setup script
├── import_data.py              # Data import script
├── advent_data_dev.json        # Development riddles
├── advent_data_prod.json       # Production riddles (excluded from git)
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .env.dev                    # Development environment (excluded from git)
├── .env.prod                   # Production environment (excluded from git)
└── .env.example                # Example environment variables
```

---

## ⚙️ Prerequisites

- **Python 3.11+** (for local development)
- **PostgreSQL database** ([NeonDB](https://neon.tech))
- **Telegram Bot Token** (from [@BotFather](https://t.me/botfather))
- **Docker & Docker Compose** (for production deployment)

---

## 💻 Installation

### Local Development

1. **Clone the repository**
```bash
   git clone https://github.com/justArale/telegram-advent-calendar-bot.git
   cd telegram-advent-calendar-bot
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Configure environment**
   
   Create `.env.dev` file:
```env
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=your_development_db_url
   TIMEZONE=preferred_timezone
   ENVIRONMENT=development
   MONTH=current_month
   ENDDAY=31
```

4. **Setup database**
```bash
   python setup_db.py dev
```

5. **Import test riddles**
```bash
   python import_data.py dev
```

6. **Run the development bot**
```bash
   python bot_dev.py
```

### Production Deployment (Docker)

1. **Clone on your server**
```bash
   git clone https://github.com/justarale/telegram-advent-calendar-bot.git
   cd telegram-advent-calendar-bot
```

2. **Create `.env.prod` file**
```env
   BOT_TOKEN=your_production_bot_token
   DATABASE_URL=your_production_db_url
   TIMEZONE=preferred_timezone
   ENVIRONMENT=prod
   MONTH=12
   ENDDAY=24
```

3. **Create your production riddles**
   
   Create `advent_data_prod.json` with your 24 riddles (on your local project):
```json
   {
     "riddles": [
       {
         "day_number": 1,
         "riddle_text": "Your riddle here",
         "answers": ["answer1", "answer2"],
         "solution_content": "🎄"
       }
     ]
   }
```

4. **Setup database**
```bash
# On your local machine
   python setup_db.py prod
```

5. **Import production riddles**
```bash
   # On your local machine
   python import_data.py prod
```

6. **Build and start container**
```bash
   docker compose up -d --build
```
---

## 🗄️ Database Schema

The project uses three main tables:

### `riddles`
```sql
id              SERIAL PRIMARY KEY
day_number      INTEGER (1-24, UNIQUE)
riddle_text     TEXT
```

### `answers`
```sql
id              SERIAL PRIMARY KEY
riddle_id       INTEGER (FOREIGN KEY → riddles.id)
answer_text     JSONB (array of valid answers)
```

### `solutions`
```sql
id              SERIAL PRIMARY KEY
riddle_id       INTEGER (FOREIGN KEY → riddles.id)
solution_content TEXT (emoji or message)
```

**Relationships**: Each riddle has one answers entry and one solutions entry.

---

## 🤖 Bot Commands

| Command | Description | Availability |
|---------|-------------|--------------|
| `/start` | Welcome message and command overview | All |
| `/riddle` | Get today's riddle | All |
| `/riddle{1-24}` | Get a specific day's riddle (e.g., `/riddle5`) | All |
| `/list` | Show all available riddles in database | Dev only |

---
## License

This project is licensed under the [MIT License](https://github.com/justArale/telegram-advent-calendar-bot/blob/main/LICENSE).
