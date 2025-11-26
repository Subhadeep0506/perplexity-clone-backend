"""Example usage of the LangGraph agent with retriever tool.

This example demonstrates how to:
1. Initialize user-specific services (vectorstore, llm, embeddings)
2. Create and run the agent with those services
3. Handle both regular and streaming responses
"""

import asyncio
from src.core.agent import run_agent, run_agent_streaming
from src.core.container import ServiceContainer
from src.core.settings import get_settings


async def example_basic_usage():
    """Basic example: Run agent with default services."""

    print("=" * 60)
    print("Example 1: Basic Agent Usage")
    print("=" * 60)

    # Initialize settings and container
    settings = get_settings()
    container = ServiceContainer(settings)

    # Get default services (for testing)
    llm = container.get_llm()
    embeddings = container.get_embeddings()
    vectorstore = container.get_vector_store(embeddings=embeddings)

    # Run the agent
    result = await run_agent(
        query="What is LangGraph and how does it work?",
        vectorstore=vectorstore,
        llm=llm,
        embeddings=embeddings,
        session_id="example_session_1",
        user_id="example_user_1",
    )

    # Print the conversation
    print("\nConversation:")
    for msg in result["messages"]:
        role = msg.__class__.__name__
        content = getattr(msg, "content", "")
        print(f"\n{role}: {content}")

    # Print retrieved documents if any
    if result.get("retrieved_docs"):
        print("\n" + "=" * 60)
        print("Retrieved Documents:")
        print("=" * 60)
        for i, doc in enumerate(result["retrieved_docs"], 1):
            print(f"\n[Doc {i}]: {doc[:200]}...")


async def example_user_specific_services():
    """Example: Run agent with user-specific API keys from database."""

    print("\n\n" + "=" * 60)
    print("Example 2: User-Specific Services")
    print("=" * 60)

    # Initialize settings and container
    settings = get_settings()
    container = ServiceContainer(settings)

    # Simulate fetching user's API key from database
    # In production, you would fetch this from your database
    user_api_key = "user_specific_api_key_from_db"
    user_id = "user_123"
    session_id = "session_456"

    # Create user-specific services with their API key
    llm = container.get_llm(api_key=user_api_key)
    embeddings = container.get_embeddings(api_key=user_api_key)
    vectorstore = container.get_vector_store(embeddings=embeddings)

    # Run the agent with user-specific configuration
    result = await run_agent(
        query="Explain the benefits of using vectorstores for retrieval",
        vectorstore=vectorstore,
        llm=llm,
        embeddings=embeddings,
        session_id=session_id,
        user_id=user_id,
        temperature=0.8,
        max_tokens=2000,
        source_type="vectorstore",
    )

    # Print results
    print(f"\nUser: {user_id}")
    print(f"Session: {session_id}")
    print("\nFinal Response:")
    final_message = result["messages"][-1]
    print(final_message.content)


async def example_streaming():
    """Example: Run agent with streaming output."""

    print("\n\n" + "=" * 60)
    print("Example 3: Streaming Agent Output")
    print("=" * 60)

    # Initialize settings and container
    settings = get_settings()
    container = ServiceContainer(settings)

    # Get services
    llm = container.get_llm()
    embeddings = container.get_embeddings()
    vectorstore = container.get_vector_store(embeddings=embeddings)

    # Run the agent with streaming
    print("\nStreaming response:\n")
    async for state_update in run_agent_streaming(
        query="What are the key components of a LangGraph agent?",
        vectorstore=vectorstore,
        llm=llm,
        embeddings=embeddings,
        session_id="streaming_session",
        user_id="streaming_user",
    ):
        # Print each state update
        print(f"Update: {state_update}")


async def example_multi_turn_conversation():
    """Example: Multi-turn conversation with context."""

    print("\n\n" + "=" * 60)
    print("Example 4: Multi-Turn Conversation")
    print("=" * 60)

    from langchain_core.messages import HumanMessage, AIMessage
    from src.core.agent import create_agent_graph
    from src.core.state.agent_state import AgentState

    # Initialize settings and container
    settings = get_settings()
    container = ServiceContainer(settings)

    # Get services
    llm = container.get_llm()
    embeddings = container.get_embeddings()
    vectorstore = container.get_vector_store(embeddings=embeddings)

    # Create agent graph
    agent_graph = create_agent_graph()

    # Initialize state
    state: AgentState = {
        "messages": [],
        "vectorstore": vectorstore,
        "llm": llm,
        "embeddings": embeddings,
        "session_id": "multi_turn_session",
        "user_id": "multi_turn_user",
        "service_id": "default",
        "api_key_id": "default",
        "temperature": 0.7,
        "max_tokens": 1000,
        "streaming": False,
        "source_type": "vectorstore",
        "retrieved_docs": None,
    }

    # First turn
    print("\n--- Turn 1 ---")
    state["messages"].append(
        HumanMessage(content="What is retrieval augmented generation?")
    )
    state = await agent_graph.ainvoke(state)
    print(f"Assistant: {state['messages'][-1].content}")

    # Second turn (with context)
    print("\n--- Turn 2 ---")
    state["messages"].append(HumanMessage(content="How does it improve LLM responses?"))
    state = await agent_graph.ainvoke(state)
    print(f"Assistant: {state['messages'][-1].content}")

    # Third turn
    print("\n--- Turn 3 ---")
    state["messages"].append(HumanMessage(content="Can you give me an example?"))
    state = await agent_graph.ainvoke(state)
    print(f"Assistant: {state['messages'][-1].content}")


async def example_with_custom_vectorstore():
    """Example: Using a custom vectorstore configuration."""

    print("\n\n" + "=" * 60)
    print("Example 5: Custom Vectorstore Configuration")
    print("=" * 60)

    from src.services.vector_store.factory import create_vector_store

    # Initialize settings and container
    settings = get_settings()
    container = ServiceContainer(settings)

    # Get LLM and embeddings
    llm = container.get_llm()
    embeddings = container.get_embeddings()

    # Create custom vectorstore with specific configuration
    custom_vectorstore = create_vector_store(
        embeddings=embeddings,
        index_name="custom_index",
        dimension=768,
        metric="cosine",
        api_key=settings.pinecone_api_key,
    )

    # Run agent with custom vectorstore
    result = await run_agent(
        query="Search for information about custom vectorstore configurations",
        vectorstore=custom_vectorstore,
        llm=llm,
        embeddings=embeddings,
        session_id="custom_vs_session",
        user_id="custom_vs_user",
    )

    print("\nResponse with custom vectorstore:")
    print(result["messages"][-1].content)


async def main():
    """Run all examples."""

    print("\n" + "=" * 60)
    print("LangGraph Agent with Retriever Tool - Examples")
    print("=" * 60)

    try:
        # Run basic example
        await example_basic_usage()

        # Run user-specific services example
        # await example_user_specific_services()

        # Run streaming example
        # await example_streaming()

        # Run multi-turn conversation example
        # await example_multi_turn_conversation()

        # Run custom vectorstore example
        # await example_with_custom_vectorstore()

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
