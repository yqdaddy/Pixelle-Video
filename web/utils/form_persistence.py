# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Form data persistence utilities.

Provides automatic saving and loading of form data to local files.
This allows users to resume their work after refreshing or reopening the page.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

# Persistence file path (in temp directory, which is in .gitignore)
PERSIST_FILE = Path("temp/form_data.json")


def save_form_data(data: Dict[str, Any]) -> None:
    """
    Save form data to local file.

    Args:
        data: Dictionary of form data to save
    """
    try:
        # Ensure temp directory exists
        PERSIST_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write to file (with atomic write to prevent corruption)
        temp_file = PERSIST_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Atomic rename
        temp_file.replace(PERSIST_FILE)

        logger.debug(f"Saved form data to {PERSIST_FILE}")

    except Exception as e:
        logger.warning(f"Failed to save form data: {e}")


def load_form_data() -> Dict[str, Any]:
    """
    Load form data from local file.

    Returns:
        Dictionary of form data, empty dict if file doesn't exist or error
    """
    try:
        if PERSIST_FILE.exists():
            with open(PERSIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Loaded form data from {PERSIST_FILE}")
                return data
    except Exception as e:
        logger.warning(f"Failed to load form data: {e}")

    return {}


def get_persisted_value(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a persisted value with session_state priority.

    Priority: session_state > persisted file > default

    Note: This function does NOT modify session_state to avoid conflicts
    with Streamlit widgets that use the same key.

    Args:
        key: The key to look up
        default: Default value if not found

    Returns:
        The value from session_state, file, or default
    """
    import streamlit as st

    # Check session_state first (highest priority)
    if key in st.session_state:
        return st.session_state[key]

    # Check persisted file (do NOT set session_state here)
    data = load_form_data()
    if key in data:
        return data[key]

    # Return default
    return default


def clear_form_data() -> None:
    """Clear all persisted form data."""
    try:
        if PERSIST_FILE.exists():
            PERSIST_FILE.unlink()
            logger.info(f"Cleared form data at {PERSIST_FILE}")
    except Exception as e:
        logger.warning(f"Failed to clear form data: {e}")


def update_form_value(key: str, value: Any) -> None:
    """
    Update a single form value and save to file.

    Note: This function only saves to file, not session_state.
    The session_state is managed by the widget itself.

    Args:
        key: The key to update
        value: The new value
    """
    # Load existing data
    data = load_form_data()

    # Update the value
    data[key] = value

    # Save back to file
    save_form_data(data)


def init_persisted_input(
    key: str,
    widget_func,
    default: Optional[Any] = None,
    **kwargs
) -> Any:
    """
    Initialize a Streamlit input widget with persisted value.

    This function wraps Streamlit input widgets (text_input, text_area, etc.)
    to automatically restore persisted values.

    Args:
        key: Widget key (used for both session_state and persistence)
        widget_func: Streamlit widget function (e.g., st.text_input)
        default: Default value if not persisted
        **kwargs: Additional arguments to pass to the widget

    Returns:
        The value from the widget

    Example:
        text = init_persisted_input(
            "user_text",
            st.text_area,
            default="",
            placeholder="Enter your text..."
        )
    """
    import streamlit as st

    # Get persisted value (checks session_state first)
    value = get_persisted_value(key, default)

    # Call the widget with the value
    result = widget_func(key=key, value=value, **kwargs)

    # Update session_state and save to file if value changed
    if result != st.session_state.get(key):
        update_form_value(key, result)

    return result