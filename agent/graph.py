from typing import Annotated, TypedDict, List

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .llm import get_chat_model
from .tools import get_tools


class AgentState(TypedDict):
	messages: Annotated[List[BaseMessage], add_messages]


def create_agent_graph():
	"""Create and compile the agent graph with a memory checkpointer."""
	tools = get_tools()
	model = get_chat_model().bind_tools(tools)

	def call_model(state: AgentState):
		response = model.invoke(state["messages"])  # Single turn model call
		return {"messages": [response]}

	builder = StateGraph(AgentState)
	builder.add_node("model", call_model)
	builder.add_node("tools", ToolNode(tools))
	builder.add_edge(START, "model")
	builder.add_conditional_edges("model", tools_condition)
	builder.add_edge("tools", "model")

	memory = MemorySaver()
	return builder.compile(checkpointer=memory)