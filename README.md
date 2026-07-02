# ✈️ AI Ticket Booking Service (FlightAI)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange?style=for-the-badge)
![OpenAI SDK](https://img.shields.io/badge/OpenAI-SDK-412991?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)
![psycopg](https://img.shields.io/badge/Driver-psycopg-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

**An asynchronous AI Agent built using Python, Gradio, PostgreSQL, SQLAlchemy Async ORM (psycopg driver), and the OpenAI SDK with Groq inference.**

</div>

---

# 📖 About the Project

FlightAI is an AI-powered airline customer support chatbot that demonstrates how to build a true **AI Agent** rather than a traditional chatbot.

Instead of simply generating an answer, the agent follows a **ReAct (Reason + Act)** workflow. Whenever it requires external information, it autonomously calls backend Python tools, queries a PostgreSQL database asynchronously, observes the returned results, and continues reasoning until it has gathered everything needed before responding.

Because of this architecture, the agent can successfully answer prompts such as:

> **"What are the ticket prices from Delhi to Mumbai, Bengaluru, Hyderabad and Chennai?"**

using multiple sequential tool calls without stopping after the first lookup.

---

# ✨ Features

- 🤖 Agentic ReAct Loop
- 🔄 Supports Multiple Sequential Tool Calls
- ⚡ Fully Asynchronous PostgreSQL Queries using SQLAlchemy Async ORM and psycopg
- 🛠️ OpenAI Function Calling
- 🧠 Autonomous Reasoning Loop
- 🗄️ Automatic Database Creation & Seeding
- 🛡️ Safe JSON Argument Parsing
- 💬 Interactive Gradio Chat Interface

---

# 🏗️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12+ |
| Frontend | Gradio ChatInterface |
| AI / LLM | OpenAI Python SDK |
| Inference | Groq API |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 Async ORM |
| Driver | psycopg |
| Environment | python-dotenv |
| Package Manager | uv |

---

# 📂 Project Structure

```text
FlightAI/
│
├── main.py
├── database.py
├── models.py
├── ticket_prices.py
├── .env
├── pyproject.toml
└── README.md
```

---

# 📋 Prerequisites

Before running the project, ensure you have the following installed:

- Python **3.12+**
- PostgreSQL running locally
- uv package manager

Install **uv**:

```bash
pip install uv
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

```env
####################################
# Groq Configuration
####################################

GROQ_API_KEY=your_api_key
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

####################################
# Gradio
####################################

GRADIO_PASSWORD=your_password

####################################
# PostgreSQL
####################################

DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flightai
```

## ⚠️ macOS Users

If PostgreSQL was installed locally on macOS, your database username is usually your **Mac username**, **not** `postgres`.

Example:

```env
DB_USERNAME=divyam
```

instead of

```env
DB_USERNAME=postgres
```

Otherwise you may encounter:

```text
FATAL: role "postgres" does not exist
```

To view your PostgreSQL roles:

```bash
psql
```

Then run:

```sql
\du
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/FlightAI.git

cd FlightAI
```

Since this project uses **uv**, dependencies are managed automatically.

The required packages include:

- openai
- gradio
- sqlalchemy
- psycopg
- greenlet
- python-dotenv

---

# ▶️ Running the Application

Start the application using:

```bash
uv run main.py
```

On startup, the application automatically:

- Creates the `ticket_prices` table
- Seeds the database with sample ticket prices
- Connects to PostgreSQL
- Launches the Gradio Chat Interface

---

# ⚙️ How It Works

Unlike a traditional chatbot, FlightAI follows a **Reason → Act → Observe** workflow.

```text
                User
                  │
                  ▼
        OpenAI / Groq LLM
                  │
          Understand Request
                  │
                  ▼
        Does it need data?
          │            │
         No           Yes
          │            │
          │            ▼
          │      Call Python Tool
          │            │
          │            ▼
          │   Query PostgreSQL
          │            │
          │            ▼
          │    Return Ticket Price
          │            │
          └────────────┤
                       ▼
          Continue Reasoning
                       │
        More Tool Calls Needed?
             │             │
            Yes            No
             │             │
             ▼             ▼
      Execute Again   Final Response
```

The agent continues executing tool calls until the language model determines it has gathered all required information.

This allows FlightAI to answer requests involving multiple destinations in a single conversation.

---

# 🧠 The ReAct Loop

The core of the application is this reasoning loop:

```python
while relevant_response.tool_calls:
    tool_responses = await call_tool(relevant_response)

    messages.append(relevant_response)
    messages.extend(tool_responses)

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    relevant_response = resp.choices[0].message
```

Instead of assuming one tool call is enough, the model repeatedly asks itself:

> **"Do I need more information?"**

If additional information is required, it automatically invokes another backend tool.

This enables:

- Multi-city ticket lookups
- Autonomous reasoning
- Sequential tool execution
- Dynamic decision making
- Reliable AI agent behavior

---

# 🗄️ Database Layer

The project uses:

- PostgreSQL
- SQLAlchemy 2.0 Async ORM
- AsyncSession
- psycopg

Database sessions are created asynchronously:

```python
async def get_session():
    async with SessionLocal() as session:
        yield session
```

Ticket prices are retrieved asynchronously:

```python
result = await session.execute(
    select(TicketPrices)
    .where(TicketPrices.city_name == city_name)
)
```

---

# 🚀 Automatic Database Seeding

When the application starts, it automatically:

- Creates the database tables
- Seeds the ticket price table
- Prevents duplicate inserts

```python
await conn.run_sync(Base.metadata.create_all)
```

This allows the project to run immediately without manually creating SQL tables.

---

# 🛠️ OpenAI Tool Calling

The LLM is provided with backend tools that it can invoke whenever additional information is required.

Example tool definition:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_price_by_city",
            "description": "Fetches ticket price by city"
        }
    }
]
```

Whenever the model needs ticket pricing information, it automatically calls:

```python
get_ticket_price_by_city(city)
```

The backend then:

1. Parses the JSON arguments.
2. Queries PostgreSQL.
3. Returns the ticket price.
4. Sends the tool result back to the LLM.
5. Continues the reasoning loop until all requested cities have been processed.

---

# 🔮 Future Enhancements

- [ ] Flight booking
- [ ] Booking cancellation
- [ ] Flight availability
- [ ] Passenger authentication
- [ ] User accounts
- [ ] Conversation memory
- [ ] Streaming responses
- [ ] Docker support
- [ ] REST API
- [ ] Unit & Integration Tests
- [ ] CI/CD Pipeline
- [ ] Monitoring & Logging
- [ ] Deployment Guide

---

# ⭐ Support

If you found this project helpful, please consider giving it a **⭐ Star** on GitHub.

It helps others discover the project and supports future development.
