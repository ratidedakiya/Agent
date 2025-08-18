# Agent

A minimal LangGraph agent with a CLI.

## Setup

1) Create and fill in your `.env` from the template:

```
cp .env.example .env
# edit .env to set OPENAI_API_KEY and model
```

2) Use a virtual environment (recommended), then install:

```
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Usage

Single message:

```
agent chat "What's the current UTC time and what's 2.5 + 7?"
```

Interactive REPL:

```
agent repl
```

You can preserve memory across calls by passing `--thread` with the same id.