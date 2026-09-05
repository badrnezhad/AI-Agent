# Persian Company AI Agent

A command-line AI assistant for answering company-related questions in Persian. It combines an OpenAI-powered agent with retrieval-augmented generation (RAG), approved Gmail sending, and live course information from the Holosen website.

## Features

- Answers users in Persian through an interactive terminal chat.
- Searches internal company policies from `data/rules.txt` using a Chroma vector store.
- Creates a short Persian execution plan before handling each request.
- Retains a small conversation history during the current session.
- Sends emails through Gmail only after explicit human approval in the terminal.
- Fetches Holosen course names and prices from the website when course-related information is requested.
- Limits agent tool-use loops to avoid runaway execution.

## Architecture

```text
CLI (main.py)
    |
    +-- Agent (agent.py)
    |     +-- OpenAI Responses API
    |     +-- Tool dispatcher (tools.py)
    |
    +-- RAG (rag.py)
          +-- rules.txt -> chunking -> OpenAI embeddings -> Chroma
          +-- semantic policy search
```

## Prerequisites

- Python 3.10 or newer
- An OpenAI API key with access to the selected chat and embedding models
- A Gmail account and an [app password](https://support.google.com/accounts/answer/185833) if you want to use email sending

## Installation

1. Clone the repository and enter the project directory.

   ```bash
   git clone https://github.com/badrnezhad/AI-Agent.git
   cd AI-Agent
   ```

2. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependencies.

   ```bash
   pip install openai python-dotenv langchain-chroma langchain-openai langchain-text-splitters requests beautifulsoup4
   ```

4. Create a `.env` file in the project root.

   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_CHAT_MODEL=gpt-4.1-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small

   # Optional: required only for the send_email tool
   GMAIL_ADDRESS=your-address@gmail.com
   GMAIL_PASSWORD=your_gmail_app_password
   ```

   The OpenAI SDK reads `OPENAI_API_KEY` automatically. Do not commit your `.env` file or credentials.

## Usage

Run the application from the repository root:

```bash
python main.py
```

On the first run, the app reads `data/rules.txt`, splits it into chunks, generates embeddings, and stores them in `db/vectors.db`. Later runs reuse that local index.

Enter your question at the prompt. Type `exit` to stop the program.

Example questions:

```text
چند روز در هفته می‌توانم دورکاری کنم؟
برای فردا یک ایمیل به team@example.com آماده کن.
دوره‌های Holosen و قیمت آن‌ها چیست؟
```

Before an email is sent, the application prints the recipient, subject, and body and asks for confirmation. Enter `yes` to send it; any other input cancels the request.

## Project Structure

```text
.
├── main.py                 # Interactive CLI entry point
├── agent.py                # Planning and OpenAI agent loop
├── tools.py                # Tool schemas and execution dispatcher
├── email_service.py        # Gmail SMTP sender
├── rag.py                  # RAG initialization and policy search
├── rag_steps/
│   ├── document.py         # Document loading, cleaning, and chunking
│   └── retrieval.py        # Chroma store and semantic retrieval
├── tool/web_search_tool.py # Holosen courses scraper
├── data/rules.txt          # Internal policies used as the RAG source
└── config.py               # Environment-driven application settings
```

## Configuration

Most settings are defined in `config.py`:

| Setting | Purpose |
| --- | --- |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Controls how policy text is split for indexing. |
| `TOP_K` | Number of relevant policy chunks returned per search. |
| `MAX_ITERATIONS` | Maximum agent tool-use iterations for one request. |
| `MAX_MEMORY_SIZE` | Number of recent messages preserved in session memory. |

To use a different model, update `OPENAI_CHAT_MODEL` or `OPENAI_EMBEDDING_MODEL` in `.env`.

## Updating Company Rules

Edit `data/rules.txt` with the new policies. Then delete the existing local vector-store directory (`db/vectors.db`) and run the application again so the documents are indexed from scratch.

## Notes

- Course information depends on the current HTML structure and availability of `https://holosen.net/courses/`.
- The Gmail integration uses SMTP over SSL on port 465.
- This is a learning/demo project; review and strengthen validation, security, observability, and error handling before using it in production.

## License

No license has been specified yet. Add a license file before distributing or reusing this project publicly.
