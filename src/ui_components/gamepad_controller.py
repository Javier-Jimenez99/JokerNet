"""
Gamepad controller component.
"""

import streamlit as st


@st.fragment
def render_gamepad_controller(api_client):
    """Visual interface for the gamepad controller."""
    st.markdown("### 🎮 Gamepad Controllers")

    # Gamepad layout
    # Top row - Triggers
    trigger_col1, trigger_col2, trigger_col3, trigger_col4 = st.columns([1, 1, 1, 1])
    with trigger_col1:
        if st.button("LT", key="lt", help="Left Trigger"):
            api_client.send_gamepad_command("LT")
    with trigger_col2:
        if st.button("LB", key="lb", help="Left Bumper"):
            api_client.send_gamepad_command("LB")
    with trigger_col3:
        if st.button("RB", key="rb", help="Right Bumper"):
            api_client.send_gamepad_command("RB")
    with trigger_col4:
        if st.button("RT", key="rt", help="Right Trigger"):
            api_client.send_gamepad_command("RT")

    st.markdown("---")

    # Main row of the gamepad
    left_section, center_section, right_section = st.columns([2, 1, 2])

    # Left section - D-Pad
    with left_section:
        st.markdown("**🕹️ D-Pad**")
        _render_dpad(api_client)

    # Center section
    with center_section:
        st.markdown("**⚙️ System**")
        _render_system_buttons(api_client)

    # Right section - Action buttons
    with right_section:
        st.markdown("**🎯 Action**")
        _render_action_buttons(api_client)


def _render_dpad(api_client):
    """Render D-Pad."""
    # D-Pad layout
    _, up_col, _ = st.columns([1, 1, 1])
    with up_col:
        if st.button("🔼", key="up", help="UP"):
            api_client.send_gamepad_command("UP")

    left_col, _, right_col = st.columns([1, 1, 1])
    with left_col:
        if st.button("◀️", key="left", help="LEFT"):
            api_client.send_gamepad_command("LEFT")
    with right_col:
        if st.button("▶️", key="right", help="RIGHT"):
            api_client.send_gamepad_command("RIGHT")

    _, down_col, _ = st.columns([1, 1, 1])
    with down_col:
        if st.button("🔽", key="down", help="DOWN"):
            api_client.send_gamepad_command("DOWN")


def _render_system_buttons(api_client):
    """Render system buttons."""
    if st.button("SELECT", key="select", help="Select Button"):
        api_client.send_gamepad_command("SELECT")

    if st.button("START", key="start", help="Start Button"):
        api_client.send_gamepad_command("START")


def _render_action_buttons(api_client):
    """Render action buttons."""
    # Xbox-style action buttons layout
    _, y_col, _ = st.columns([1, 1, 1])
    with y_col:
        if st.button("Y", key="y", help="Y Button - Yellow"):
            api_client.send_gamepad_command("Y")

    x_col, _, b_col = st.columns([1, 1, 1])
    with x_col:
        if st.button("X", key="x", help="X Button - Blue"):
            api_client.send_gamepad_command("X")
    with b_col:
        if st.button("B", key="b", help="B Button - Red"):
            api_client.send_gamepad_command("B")

    _, a_col, _ = st.columns([1, 1, 1])
    with a_col:
        if st.button("A", key="a", help="A Button - Green"):
            api_client.send_gamepad_command("A")