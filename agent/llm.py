import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def get_chat_model(temperature: float = 0.0, model_name: Optional[str] = None) -> ChatOpenAI:
	"""Create a ChatOpenAI model configured from environment variables.

	Environment variables:
	- OPENAI_API_KEY
	- OPENAI_MODEL (default: gpt-4o-mini)
	- OPENAI_BASE_URL (optional)
	"""
	api_key = os.getenv("OPENAI_API_KEY")
	base_url = os.getenv("OPENAI_BASE_URL")
	resolved_model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	if not api_key:
		raise RuntimeError("OPENAI_API_KEY is not set. Create a .env with your key or export it.")

	if base_url:
		return ChatOpenAI(api_key=api_key, base_url=base_url, model=resolved_model_name, temperature=temperature)
	return ChatOpenAI(api_key=api_key, model=resolved_model_name, temperature=temperature)