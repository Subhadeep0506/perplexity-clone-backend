"""LangGraph Agent implementation with retriever tool and user-specific services.

This module demonstrates how to create a LangGraph agent that:
1. Uses a retriever tool to fetch content from a vectorstore
2. Passes user-specific services (vectorstore, llm, embeddings) through state
3. Handles tool calls and generates responses
"""

from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.core.state.agent_state import AgentState
from src.core.tools.retriever_tool import retriever_tool


def create_agent_graph():
    """Create a LangGraph agent with retriever tool.

    The agent graph includes:
    - An agent node that decides whether to use tools or respond
    - A tool node that executes the retriever tool
    - Conditional edges for routing between nodes

    Returns:
        Compiled StateGraph ready for execution
    """

    # Define the agent node
    async def agent_node(state: AgentState) -> AgentState:
        """Agent node that processes messages and decides on tool usage.

        This node:
        1. Gets the LLM from state (user-specific)
        2. Binds tools to the LLM
        3. Invokes the LLM with conversation history
        4. Returns updated state with LLM response
        """
        llm = state.get("llm")

        if not llm:
            # Fallback error message if LLM is not initialized
            return {
                "messages": [
                    AIMessage(
                        content="Error: No LLM available. Please initialize an LLM in the state."
                    )
                ]
            }

        # Get the conversation messages
        messages = state.get("messages", [])

        # Bind tools to the LLM - pass the tool directly
        # LangChain will handle the conversion based on the LLM provider
        llm_with_tools = llm.bind_tools([retriever_tool])

        # Invoke the LLM
        response = await llm_with_tools.ainvoke(messages)

        # Return updated state with the LLM's response
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine whether to continue to tools or end.

        Args:
            state: Current agent state

        Returns:
            "tools" if the last message has tool calls, "end" otherwise
        """
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None

        # If the last message has tool calls, route to tools
        if (
            last_message
            and hasattr(last_message, "tool_calls")
            and last_message.tool_calls
        ):
            return "tools"

        # Otherwise, end the conversation
        return "end"

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)

    # Create tool node with the retriever tool
    # The ToolNode automatically handles tool execution and state injection
    tool_node = ToolNode([retriever_tool])
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile the graph
    return workflow.compile()


async def run_agent(
    query: str,
    vectorstore,
    llm,
    embeddings=None,
    session_id: str = "default",
    user_id: str = "default",
    **kwargs,
) -> dict:
    """Run the agent with a query and user-specific services.

    Args:
        query: The user's query
        vectorstore: User-specific vectorstore instance
        llm: User-specific LLM instance
        embeddings: Optional user-specific embeddings instance
        session_id: Session identifier
        user_id: User identifier
        **kwargs: Additional state parameters

    Returns:
        Final state after agent execution

    Example:
        >>> from src.core.container import ServiceContainer
        >>> from src.core.settings import get_settings
        >>>
        >>> # Initialize services based on user choice
        >>> settings = get_settings()
        >>> container = ServiceContainer(settings)
        >>>
        >>> # Get user-specific services (with user's API keys from DB)
        >>> user_api_key = "user_api_key_from_db"
        >>> llm = container.get_llm(api_key=user_api_key)
        >>> embeddings = container.get_embeddings(api_key=user_api_key)
        >>> vectorstore = container.get_vector_store(embeddings=embeddings)
        >>>
        >>> # Run the agent
        >>> result = await run_agent(
        ...     query="What is LangGraph?",
        ...     vectorstore=vectorstore,
        ...     llm=llm,
        ...     embeddings=embeddings,
        ...     session_id="session_123",
        ...     user_id="user_456"
        ... )
        >>>
        >>> # Get the final response
        >>> final_message = result["messages"][-1]
        >>> print(final_message.content)
    """

    # Create the agent graph
    agent_graph = create_agent_graph()

    # Initialize state with user-specific services
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "vectorstore": vectorstore,
        "llm": llm,
        "embeddings": embeddings,
        "session_id": session_id,
        "user_id": user_id,
        "service_id": kwargs.get("service_id", "default"),
        "api_key_id": kwargs.get("api_key_id", "default"),
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 1000),
        "streaming": kwargs.get("streaming", False),
        "source_type": kwargs.get("source_type", "vectorstore"),
        "retrieved_docs": None,
    }

    # Run the agent
    final_state = await agent_graph.ainvoke(initial_state)

    return final_state


async def run_agent_streaming(
    query: str,
    vectorstore,
    llm,
    embeddings=None,
    session_id: str = "default",
    user_id: str = "default",
    **kwargs,
):
    """Run the agent with streaming output.

    Args:
        query: The user's query
        vectorstore: User-specific vectorstore instance
        llm: User-specific LLM instance
        embeddings: Optional user-specific embeddings instance
        session_id: Session identifier
        user_id: User identifier
        **kwargs: Additional state parameters

    Yields:
        State updates as they occur

    Example:
        >>> async for state_update in run_agent_streaming(
        ...     query="Explain LangGraph",
        ...     vectorstore=vectorstore,
        ...     llm=llm,
        ...     session_id="session_123"
        ... ):
        ...     print(state_update)
    """

    # Create the agent graph
    agent_graph = create_agent_graph()

    # Initialize state with user-specific services
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "vectorstore": vectorstore,
        "llm": llm,
        "embeddings": embeddings,
        "session_id": session_id,
        "user_id": user_id,
        "service_id": kwargs.get("service_id", "default"),
        "api_key_id": kwargs.get("api_key_id", "default"),
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 1000),
        "streaming": kwargs.get("streaming", True),
        "source_type": kwargs.get("source_type", "vectorstore"),
        "retrieved_docs": None,
    }

    # Stream the agent execution
    async for state_update in agent_graph.astream(initial_state):
        yield state_update
