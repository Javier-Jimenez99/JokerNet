"""
Chat component for AI interaction.
"""

import streamlit as st
import asyncio
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from streamlit.delta_generator import DeltaGenerator
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from typing import Callable, TypeVar
import inspect
import json
import base64
import io

from .gamepad_controller import render_gamepad_controller
from .agent import format_worker_result_for_chat
from langchain_core.messages import HumanMessage

def display_messages():
    """Display the conversation history."""
    for msg in st.session_state.chat_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)


@st.fragment
def render_chat_block():
    """Render chat block."""
    # Fixed height container for chat (messages only)
    main_container = st.container(height=650)
    with main_container:
        display_messages()

    # User input outside the message container
    if user_input := st.chat_input(placeholder="Describe the task you want to perform..."):
        # Add user message to history
        history = st.session_state.get("chat_history", [])
        history.append(HumanMessage(content=user_input))
        st.session_state.chat_history = history

        with main_container:
            st.chat_message("user").markdown(user_input)

            with st.chat_message("assistant"):
                config = {
                    "recursion_limit": st.session_state.max_iterations,
                    "configurable": {"max_iterations": st.session_state.max_iterations},
                    "callbacks": [get_streamlit_cb(st.empty(), debug_mode=st.session_state.debug_mode)]
                }

                try:
                    with st.spinner("Running agent..."):
                        response = asyncio.run(
                            st.session_state.agent.ainvoke(
                                input={
                                    "input": history
                                },
                                config=config
                            )
                        )
                        # Get the worker result
                        if "result" in response and response["output"]:
                            result = response["output"]
                        else:
                            result = "Could not get a result from the agent."

                        st.markdown(result)
                        st.session_state.chat_history.append(
                            AIMessage(content=result)
                        )
                except Exception as e:
                    print("Exception occurred in render_chat_block", e)
                    error_msg = f"Error processing request ({type(e).__name__}): {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})


def render_chat_interface():
    """Render chat interface with contextual information."""
    if "agent" not in st.session_state:
        st.info("Initializing AI agent...")
        return

    # Render chat
    render_chat_block()

class LanggraphCallbackHandler(BaseCallbackHandler):
    def __init__(self, parent_container: DeltaGenerator):
        self.expander = parent_container.expander("📤 Model Processing")

    def on_chain_start(self, serialized, input_str, **kwargs):
        node = kwargs.get("name", "unknown")

        if node == "planner":
            self.expander.write("🧠 **Running Planner**")  
        elif node == "worker_visualizer":
            self.expander.write("👁️ **Running Worker Visualizer**")
        elif node == "planner_visualizer":
            self.expander.write("👁️ **Running Planner Visualizer**")
        elif node == "worker":
            self.expander.write("🧑�‍💻 **Running Worker**")
        elif node == "tool":
            self.expander.write("🔧 **Running Tool**")
        elif node == "output":
            self.expander.write("🏁 **Generating Output**")

class CustomToolCallbackHandler(BaseCallbackHandler):
    """Custom callback to show tool calls."""

    def __init__(self, parent_container):
        self.parent_container = parent_container
        self.current_tool_expander = None
        self.tool_counter = 0

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool execution starts."""
        self.tool_counter += 1
        tool_name = serialized.get('name', 'Unknown Tool')

        self.current_tool_expander = self.parent_container.expander(
            f"🔧 Tool #{self.tool_counter}: {tool_name}",
            expanded=True
        )

        with self.current_tool_expander:
            st.write("**📥 Input:**")
            if isinstance(input_str, str) and len(input_str) > 500:
                with st.expander("View full input", expanded=False):
                    st.code(input_str)
            else:
                st.code(str(input_str))

    def on_tool_end(self, output, **kwargs):
        """Called when a tool execution ends."""
        if self.current_tool_expander is None:
            return

        with self.current_tool_expander:
            st.write("**📤 Output:**")

            if hasattr(output, 'artifact') and output.artifact:
                for artifact in output.artifact:
                    if artifact.type == "image":
                        if isinstance(artifact.data, str) and self._looks_like_b64(artifact.data):
                            st.write("🖼️ **Generated image:**")
                            self._render_b64(artifact.data)
                        else:
                            st.error("Artifact is not a valid base64 image.")
                    else:
                        st.write(f"📄 **Artifact ({artifact.type}):**")
                        st.code(str(artifact.data))

                if hasattr(output, 'content') and output.content:
                    st.write("**💬 Content:**")
                    st.code(output.content)
            else:
                output_str = str(output)
                if len(output_str) > 1000:
                    with st.expander("View full output", expanded=False):
                        st.code(output_str)
                else:
                    st.code(output_str)

    def on_tool_error(self, error, **kwargs):
        """Called when there is an error in the tool."""
        if self.current_tool_expander is None:
            return

        with self.current_tool_expander:
            st.write("**❌ Error:**")
            st.error(str(error))

    @staticmethod
    def _looks_like_b64(s: str) -> bool:
        """Check if a string looks like base64."""
        return (
            s.startswith("data:image")
            or (len(s) % 4 == 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in s[:64]))
        )

    def _render_b64(self, data: str):
        """Render a base64 image."""
        try:
            head, _, body = data.partition(",")
            b = base64.b64decode(body if _ else data)
            st.image(io.BytesIO(b), caption="Screenshot", use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")

    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Show messages sent to the model if debug mode is enabled."""
        batch = messages[0] if messages and len(messages) > 0 else []
        snapshot = []

        for m in batch:
            if isinstance(m.content, list):
                parts = []
                for p in m.content:
                    if isinstance(p, dict) and p.get("type") in ("image_url", "input_image", "image"):
                        preview = (p.get("image_url", {}).get("url") or "")[:80]
                        parts.append({"type": p["type"], "preview": preview + "..."})
                    else:
                        parts.append({"type": p.get("type", "text"), "text": str(p.get("text", ""))[:160]})
                snapshot.append({"role": m.type, "content": parts})
            else:
                snapshot.append({"role": m.type, "text": str(m.content)[:400]})

        with self.parent_container.expander("📤 Messages sent to model", expanded=False):
            st.code(json.dumps(snapshot, ensure_ascii=False, indent=2))


def get_streamlit_cb(parent_container: DeltaGenerator, debug_mode: bool = False) -> BaseCallbackHandler:
    """Create callback handler with Streamlit context."""
    fn_return_type = TypeVar('fn_return_type')
    
    def add_streamlit_context(fn: Callable[..., fn_return_type]) -> Callable[..., fn_return_type]:
        ctx = get_script_run_ctx()

        def wrapper(*args, **kwargs) -> fn_return_type:
            add_script_run_ctx(ctx=ctx)
            return fn(*args, **kwargs)

        return wrapper

    if debug_mode:
        st_cb = CustomToolCallbackHandler(parent_container)
    st_cb = LanggraphCallbackHandler(parent_container)

    for method_name, method_func in inspect.getmembers(st_cb, predicate=inspect.ismethod):
        if method_name.startswith('on_'):
            setattr(st_cb, method_name, add_streamlit_context(method_func))
    return st_cb


def render_chat(api_client):
    """Render control tabs (Chat and Manual Controls)."""
    if "agent" not in st.session_state:
        st.info("Initializing AI agent...")
        return

    # Create tabs for Chat and Controls
    chat_tab, controls_tab = st.tabs(["💬 AI Chat", "🎮 Gamepad Controllers"])

    with chat_tab:
        render_chat_interface()

    with controls_tab:
        render_gamepad_controller(api_client)