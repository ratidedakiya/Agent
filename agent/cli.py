import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from langchain_core.messages import HumanMessage

from .graph import create_agent_graph


load_dotenv()
app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

def _print_markdown(text: str) -> None:
	if not text:
		return
	console.print(Markdown(text))


@app.command(help="Send one message to the agent and print the reply.")
def chat(
	message: str = typer.Argument(..., help="User message to send to the agent"),
	thread: str = typer.Option("cli", "--thread", help="Thread id to preserve memory across calls"),
):
	graph = create_agent_graph()
	config = {"configurable": {"thread_id": thread}}
	last_text: Optional[str] = None
	for state in graph.stream({"messages": [HumanMessage(content=message)]}, config, stream_mode="values"):
		msg = state["messages"][-1]
		last_text = getattr(msg, "content", None)
	_print_markdown(last_text or "")


@app.command(help="Start an interactive REPL with the agent.")
def repl(thread: str = typer.Option("repl", "--thread", help="Thread id for the REPL session")):
	console.print("Type 'exit' or 'quit' to leave.")
	graph = create_agent_graph()
	config = {"configurable": {"thread_id": thread}}
	while True:
		try:
			user = console.input("[bold green]You[/]: ")
		except (EOFError, KeyboardInterrupt):
			break
		if user.strip().lower() in {"exit", "quit"}:
			break
		last_text: Optional[str] = None
		for state in graph.stream({"messages": [HumanMessage(content=user)]}, config, stream_mode="values"):
			msg = state["messages"][-1]
			last_text = getattr(msg, "content", None)
		_print_markdown(last_text or "")


if __name__ == "__main__":
	app()