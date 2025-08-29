import streamlit as st
import asyncio
from agents import create_agent as create_langgraph_agent



@st.cache_resource
def create_agent():
    """Create Worker agent."""
    mcp_type = st.session_state.get("mcp_type", "gamepad")
    max_worker_steps = st.session_state.get("max_worker_steps", 3)
    max_planner_steps = st.session_state.get("max_planner_steps", 5)

    async def _create():
        agent = await create_langgraph_agent(
            server_name=mcp_type,
            max_worker_steps=max_worker_steps,
            max_planner_steps=max_planner_steps
        )
        return agent

    return asyncio.run(_create())



def recreate_agent():
    """Recreate agent when configuration changes."""
    create_agent.clear()
    with st.spinner("Reconfiguring AI agent..."):
        st.session_state.agent = create_agent()
    st.session_state.chat_history = []


def format_worker_result_for_chat(result):
    """Format the worker result to display in the chat."""
    if not result:
        return "Could not get a result from the worker."

    success = result.get("success", False)
    reason = result.get("reason", "unknown")
    iterations = result.get("iterations", 0)
    description = result.get("description", "")

    if success:
        chat_message = f"✅ Task completed: {reason}\n\n{description}"
    else:
        chat_message = f"❌ Task failed: {reason}\n\n{description}"

    chat_message += f"\n\n📊 Iterations: {iterations}"

    if "worker_reasoning" in result:
        chat_message += f"\n\n🧠 Reasoning: {result['worker_reasoning']}"

    return chat_message