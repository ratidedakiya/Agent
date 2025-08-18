from datetime import datetime, timezone
from typing import List

from langchain_core.tools import tool


@tool
def add_numbers(a: float, b: float) -> float:
	"""Add two numbers and return the sum."""
	return a + b


@tool
def current_time_utc() -> str:
	"""Return the current UTC time as an ISO 8601 string."""
	now = datetime.now(timezone.utc)
	return now.isoformat()


def get_tools() -> List:
	"""Return the list of tool callables to bind to the model."""
	return [add_numbers, current_time_utc]